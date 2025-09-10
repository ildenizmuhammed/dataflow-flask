// WebRTC integration for DataFlow Spaces
class WebRTCConference {
    constructor() {
        this.localStream = null;
        this.remoteStreams = new Map();
        this.peerConnections = new Map();
        this.roomId = null;
        this.participantId = null;
        this.isMuted = false;
        this.isVideoEnabled = true;
        
        // FreeSWITCH WebRTC server configuration
        this.freeswitchConfig = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        };
        
        this.initializeElements();
    }
    
    initializeElements() {
        this.localVideo = document.getElementById('localVideo');
        this.remoteVideos = document.getElementById('remoteVideos');
        this.muteButton = document.getElementById('muteButton');
        this.videoButton = document.getElementById('videoButton');
        this.leaveButton = document.getElementById('leaveButton');
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        if (this.muteButton) {
            this.muteButton.addEventListener('click', () => this.toggleMute());
        }
        
        if (this.videoButton) {
            this.videoButton.addEventListener('click', () => this.toggleVideo());
        }
        
        if (this.leaveButton) {
            this.leaveButton.addEventListener('click', () => this.leaveConference());
        }
    }
    
    async joinConference(roomId, participantId) {
        try {
            this.roomId = roomId;
            this.participantId = participantId;
            
            // Get user media
            this.localStream = await navigator.mediaDevices.getUserMedia({
                audio: true,
                video: true
            });
            
            if (this.localVideo) {
                this.localVideo.srcObject = this.localStream;
            }
            
            // Connect to FreeSWITCH via WebRTC
            await this.connectToFreeSWITCH();
            
            console.log('Successfully joined conference:', roomId);
            return true;
            
        } catch (error) {
            console.error('Error joining conference:', error);
            this.showError('Konferansa katılırken hata oluştu: ' + error.message);
            return false;
        }
    }
    
    async connectToFreeSWITCH() {
        try {
            // Create WebRTC connection to FreeSWITCH
            const peerConnection = new RTCPeerConnection(this.freeswitchConfig);
            
            // Add local stream
            this.localStream.getTracks().forEach(track => {
                peerConnection.addTrack(track, this.localStream);
            });
            
            // Handle remote streams
            peerConnection.ontrack = (event) => {
                const remoteStream = event.streams[0];
                this.addRemoteStream(remoteStream, event.track.id);
            };
            
            // Handle ICE candidates
            peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    this.sendIceCandidate(event.candidate);
                }
            };
            
            // Create offer
            const offer = await peerConnection.createOffer();
            await peerConnection.setLocalDescription(offer);
            
            // Send offer to FreeSWITCH via Flask API
            const response = await fetch('/api/webrtc/offer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    room_id: this.roomId,
                    participant_id: this.participantId,
                    offer: offer
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                await peerConnection.setRemoteDescription(data.answer);
                
                // Store connection
                this.peerConnections.set(this.participantId, peerConnection);
            } else {
                throw new Error('Failed to establish WebRTC connection');
            }
            
        } catch (error) {
            console.error('FreeSWITCH connection error:', error);
            throw error;
        }
    }
    
    addRemoteStream(stream, trackId) {
        const videoElement = document.createElement('video');
        videoElement.srcObject = stream;
        videoElement.autoplay = true;
        videoElement.muted = true; // Prevent echo
        videoElement.className = 'remote-video';
        
        if (this.remoteVideos) {
            this.remoteVideos.appendChild(videoElement);
        }
        
        this.remoteStreams.set(trackId, stream);
    }
    
    toggleMute() {
        if (this.localStream) {
            const audioTrack = this.localStream.getAudioTracks()[0];
            if (audioTrack) {
                audioTrack.enabled = !audioTrack.enabled;
                this.isMuted = !audioTrack.enabled;
                
                if (this.muteButton) {
                    this.muteButton.textContent = this.isMuted ? '🔇 Unmute' : '🔊 Mute';
                }
                
                // Notify server
                this.sendMuteStatus(this.isMuted);
            }
        }
    }
    
    toggleVideo() {
        if (this.localStream) {
            const videoTrack = this.localStream.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = !videoTrack.enabled;
                this.isVideoEnabled = videoTrack.enabled;
                
                if (this.videoButton) {
                    this.videoButton.textContent = this.isVideoEnabled ? '📹 Video Off' : '📹 Video On';
                }
                
                // Notify server
                this.sendVideoStatus(this.isVideoEnabled);
            }
        }
    }
    
    async leaveConference() {
        try {
            // Stop local stream
            if (this.localStream) {
                this.localStream.getTracks().forEach(track => track.stop());
            }
            
            // Close peer connections
            this.peerConnections.forEach(connection => {
                connection.close();
            });
            
            // Clear streams
            this.remoteStreams.clear();
            this.peerConnections.clear();
            
            // Notify server
            await fetch('/api/webrtc/leave', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    room_id: this.roomId,
                    participant_id: this.participantId
                })
            });
            
            console.log('Left conference successfully');
            
        } catch (error) {
            console.error('Error leaving conference:', error);
        }
    }
    
    sendIceCandidate(candidate) {
        // Send ICE candidate to server
        fetch('/api/webrtc/ice-candidate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                room_id: this.roomId,
                participant_id: this.participantId,
                candidate: candidate
            })
        }).catch(error => {
            console.error('Error sending ICE candidate:', error);
        });
    }
    
    sendMuteStatus(isMuted) {
        fetch('/api/webrtc/mute-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                room_id: this.roomId,
                participant_id: this.participantId,
                is_muted: isMuted
            })
        }).catch(error => {
            console.error('Error sending mute status:', error);
        });
    }
    
    sendVideoStatus(isVideoEnabled) {
        fetch('/api/webrtc/video-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                room_id: this.roomId,
                participant_id: this.participantId,
                is_video_enabled: isVideoEnabled
            })
        }).catch(error => {
            console.error('Error sending video status:', error);
        });
    }
    
    showError(message) {
        // Show error message to user
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ff4444;
            color: white;
            padding: 15px;
            border-radius: 5px;
            z-index: 1000;
        `;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            document.body.removeChild(errorDiv);
        }, 5000);
    }
}

// Initialize WebRTC when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.webrtcConference = new WebRTCConference();
});
