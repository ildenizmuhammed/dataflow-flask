// WebRTC Audio Conference Manager for Clubhouse-style app
class WebRTCAudioConference {
    constructor() {
        this.localStream = null;
        this.remoteStreams = new Map();
        this.peerConnections = new Map();
        this.roomId = null;
        this.userId = null;
        this.isMuted = false;
        this.isSpeaking = false;
        
        // ICE servers configuration
        this.iceServers = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' },
                { urls: 'stun:stun2.l.google.com:19302' }
            ]
        };
        
        // Audio context for better audio processing
        this.audioContext = null;
        this.audioAnalyser = null;
        this.speakingThreshold = -50; // dB threshold for speaking detection
    }
    
    async initialize() {
        try {
            // Get user media (audio only for Clubhouse style)
            this.localStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 44100
                },
                video: false
            });
            
            // Set up audio context for speaking detection
            this.setupAudioContext();
            
            console.log('WebRTC Audio initialized successfully');
            return true;
        } catch (error) {
            console.error('Error initializing WebRTC Audio:', error);
            return false;
        }
    }
    
    setupAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = this.audioContext.createMediaStreamSource(this.localStream);
            this.audioAnalyser = this.audioContext.createAnalyser();
            this.audioAnalyser.fftSize = 256;
            source.connect(this.audioAnalyser);
            
            // Start speaking detection
            this.startSpeakingDetection();
        } catch (error) {
            console.error('Error setting up audio context:', error);
        }
    }
    
    startSpeakingDetection() {
        const dataArray = new Uint8Array(this.audioAnalyser.frequencyBinCount);
        
        const detectSpeaking = () => {
            this.audioAnalyser.getByteFrequencyData(dataArray);
            
            // Calculate average volume
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                sum += dataArray[i];
            }
            const average = sum / dataArray.length;
            const volume = 20 * Math.log10(average / 255);
            
            // Detect speaking
            const wasSpeaking = this.isSpeaking;
            this.isSpeaking = volume > this.speakingThreshold && !this.isMuted;
            
            // Notify if speaking state changed
            if (this.isSpeaking !== wasSpeaking) {
                this.onSpeakingStateChanged(this.isSpeaking);
            }
            
            requestAnimationFrame(detectSpeaking);
        };
        
        detectSpeaking();
    }
    
    onSpeakingStateChanged(isSpeaking) {
        // Emit to socket for real-time updates
        if (window.socket && this.roomId && this.userId) {
            if (isSpeaking) {
                window.socket.emit('start_speaking', { 
                    room_id: this.roomId, 
                    user_id: this.userId 
                });
            } else {
                window.socket.emit('stop_speaking', { 
                    room_id: this.roomId, 
                    user_id: this.userId 
                });
            }
        }
    }
    
    async joinRoom(roomId, userId) {
        this.roomId = roomId;
        this.userId = userId;
        
        try {
            // Initialize WebRTC
            const initialized = await this.initialize();
            if (!initialized) {
                return false;
            }
            
            // Get existing room members
            const response = await fetch(`/api/rooms/${roomId}/members`);
            if (response.ok) {
                const members = await response.json();
                
                // Create peer connections for existing members
                for (const member of members) {
                    if (member.user_id !== userId) {
                        await this.createPeerConnection(member.user_id);
                    }
                }
            }
            
            return true;
        } catch (error) {
            console.error('Error joining room:', error);
            return false;
        }
    }
    
    async createPeerConnection(userId) {
        const peerConnection = new RTCPeerConnection(this.iceServers);
        this.peerConnections.set(userId, peerConnection);
        
        // Add local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => {
                peerConnection.addTrack(track, this.localStream);
            });
        }
        
        // Handle remote streams
        peerConnection.ontrack = (event) => {
            const remoteStream = event.streams[0];
            this.remoteStreams.set(userId, remoteStream);
            this.updateAudioElements();
        };
        
        // Handle ICE candidates
        peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.sendIceCandidate(userId, event.candidate);
            }
        };
        
        // Create offer
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        
        // Send offer to the other user via signaling server
        await this.sendOffer(userId, offer);
        
        return peerConnection;
    }
    
    async sendOffer(userId, offer) {
        try {
            const response = await fetch('/api/webrtc/offer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    room_id: this.roomId,
                    from_user_id: this.userId,
                    to_user_id: userId,
                    offer: offer
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.answer) {
                    await this.handleAnswer(userId, data.answer);
                }
            }
        } catch (error) {
            console.error('Error sending offer:', error);
        }
    }
    
    async handleAnswer(userId, answer) {
        const peerConnection = this.peerConnections.get(userId);
        if (peerConnection) {
            await peerConnection.setRemoteDescription(answer);
        }
    }
    
    async sendIceCandidate(userId, candidate) {
        try {
            await fetch('/api/webrtc/ice-candidate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    room_id: this.roomId,
                    from_user_id: this.userId,
                    to_user_id: userId,
                    candidate: candidate
                })
            });
        } catch (error) {
            console.error('Error sending ICE candidate:', error);
        }
    }
    
    updateAudioElements() {
        // Create hidden audio elements for each remote stream
        this.remoteStreams.forEach((stream, userId) => {
            let audioElement = document.getElementById(`audio-${userId}`);
            if (!audioElement) {
                audioElement = document.createElement('audio');
                audioElement.id = `audio-${userId}`;
                audioElement.autoplay = true;
                audioElement.playsInline = true;
                audioElement.volume = 0.8; // Default volume
                document.body.appendChild(audioElement);
            }
            audioElement.srcObject = stream;
        });
    }
    
    toggleMute() {
        if (this.localStream) {
            const audioTracks = this.localStream.getAudioTracks();
            audioTracks.forEach(track => {
                track.enabled = !track.enabled;
            });
            this.isMuted = !this.isMuted;
            
            // Update speaking state
            if (this.isMuted) {
                this.isSpeaking = false;
                this.onSpeakingStateChanged(false);
            }
            
            return this.isMuted;
        }
        return false;
    }
    
    setMute(muted) {
        if (this.localStream) {
            const audioTracks = this.localStream.getAudioTracks();
            audioTracks.forEach(track => {
                track.enabled = !muted;
            });
            this.isMuted = muted;
            
            if (muted) {
                this.isSpeaking = false;
                this.onSpeakingStateChanged(false);
            }
        }
    }
    
    setVolume(userId, volume) {
        const audioElement = document.getElementById(`audio-${userId}`);
        if (audioElement) {
            audioElement.volume = Math.max(0, Math.min(1, volume));
        }
    }
    
    async handleNewMember(userId) {
        // Create peer connection for new member
        await this.createPeerConnection(userId);
    }
    
    async handleMemberLeft(userId) {
        // Close peer connection and remove audio element
        const peerConnection = this.peerConnections.get(userId);
        if (peerConnection) {
            peerConnection.close();
            this.peerConnections.delete(userId);
        }
        
        this.remoteStreams.delete(userId);
        
        const audioElement = document.getElementById(`audio-${userId}`);
        if (audioElement) {
            audioElement.remove();
        }
    }
    
    async leaveRoom() {
        try {
            // Close all peer connections
            this.peerConnections.forEach(connection => {
                connection.close();
            });
            this.peerConnections.clear();
            
            // Stop local stream
            if (this.localStream) {
                this.localStream.getTracks().forEach(track => {
                    track.stop();
                });
                this.localStream = null;
            }
            
            // Clear remote streams and audio elements
            this.remoteStreams.forEach((stream, userId) => {
                const audioElement = document.getElementById(`audio-${userId}`);
                if (audioElement) {
                    audioElement.remove();
                }
            });
            this.remoteStreams.clear();
            
            // Close audio context
            if (this.audioContext) {
                await this.audioContext.close();
                this.audioContext = null;
            }
            
            console.log('Left room successfully');
        } catch (error) {
            console.error('Error leaving room:', error);
        }
    }
}

// Initialize WebRTC Audio Conference when page loads
window.addEventListener('DOMContentLoaded', function() {
    window.webrtcAudioConference = new WebRTCAudioConference();
});