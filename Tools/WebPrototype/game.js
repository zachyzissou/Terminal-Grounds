/**
 * Terminal Grounds - Web Prototype Game Engine
 * Complete territorial warfare implementation using our backend systems
 * 
 * Features:
 * - Real-time multiplayer via WebSocket (connects to our existing server)
 * - All three maps: Metro Junction, IEZ Frontier, Wasteland Crossroads
 * - Seven faction territorial warfare
 * - Extraction mechanics with territorial influence
 * - Live territorial balance validation
 */

class TerminalGroundsGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.websocket = null;
        this.playerId = null;
        this.playerFaction = null;
        this.playerPosition = { x: 400, y: 300 };
        this.currentMap = 'metro';
        this.territories = new Map();
        this.players = new Map();
        this.extractionProgress = 0;
        this.extractionActive = false;
        this.extractionTarget = null;
        
        this.factions = {
            1: { name: 'Directorate', color: '#3366ff', shortName: 'DIR' },
            2: { name: 'Free77', color: '#ff3333', shortName: 'F77' },
            3: { name: 'Nomad Clans', color: '#ffaa33', shortName: 'NOM' },
            4: { name: 'Civic Wardens', color: '#aaaaaa', shortName: 'CIV' },
            5: { name: 'Vultures Union', color: '#aa3366', shortName: 'VUL' },
            6: { name: 'Vaulted Archivists', color: '#33aaff', shortName: 'ARC' },
            7: { name: 'Corporate Hegemony', color: '#663399', shortName: 'HEG' }
        };

        // Map configurations from our territorial system
        this.maps = {
            metro: {
                name: 'Metro Junction',
                size: { width: 800, height: 600 },
                territories: [
                    { id: 1001, name: 'Metro Region', x: 400, y: 300, radius: 200, type: 'region' },
                    { id: 1002, name: 'Directorate Zone', x: 200, y: 300, radius: 100, type: 'district', faction: 1 },
                    { id: 1003, name: 'Free77 Zone', x: 600, y: 300, radius: 100, type: 'district', faction: 2 },
                    { id: 1004, name: 'Central Hub', x: 400, y: 200, radius: 75, type: 'district', contested: true },
                    { id: 1005, name: 'Platform Alpha', x: 150, y: 400, radius: 50, type: 'extraction', faction: 1 },
                    { id: 1007, name: 'Platform Beta', x: 650, y: 400, radius: 50, type: 'extraction', faction: 2 }
                ]
            },
            iez: {
                name: 'IEZ Frontier',
                size: { width: 1200, height: 1000 },
                territories: [
                    { id: 2001, name: 'IEZ Region', x: 600, y: 500, radius: 300, type: 'region' },
                    { id: 2002, name: 'Corporate District', x: 300, y: 500, radius: 150, type: 'district', faction: 7 },
                    { id: 2003, name: 'Nomad Territory', x: 900, y: 700, radius: 125, type: 'district', faction: 3 },
                    { id: 2004, name: 'Industrial Core', x: 600, y: 300, radius: 100, type: 'district', contested: true },
                    { id: 2006, name: 'Corporate Facility', x: 200, y: 400, radius: 60, type: 'extraction', faction: 7 },
                    { id: 2009, name: 'Nomad Basecamp', x: 1000, y: 800, radius: 60, type: 'extraction', faction: 3 }
                ]
            },
            wasteland: {
                name: 'Wasteland Crossroads',
                size: { width: 1600, height: 1400 },
                territories: [
                    { id: 3001, name: 'Wasteland Region', x: 800, y: 700, radius: 400, type: 'region' },
                    { id: 3002, name: 'Directorate Outpost', x: 300, y: 400, radius: 100, type: 'district', faction: 1 },
                    { id: 3003, name: 'Free77 Camp', x: 1200, y: 300, radius: 100, type: 'district', faction: 2 },
                    { id: 3004, name: 'Nomad Territory', x: 1100, y: 1200, radius: 125, type: 'district', faction: 3 },
                    { id: 3005, name: 'Civic Refuge', x: 600, y: 1100, radius: 90, type: 'district', faction: 4 },
                    { id: 3006, name: 'Vultures Scrapyard', x: 200, y: 900, radius: 110, type: 'district', faction: 5 },
                    { id: 3007, name: 'Archivists Vault', x: 1400, y: 600, radius: 75, type: 'district', faction: 6 },
                    { id: 3008, name: 'Corporate Zone', x: 700, y: 200, radius: 150, type: 'district', faction: 7 }
                ]
            }
        };

        this.init();
    }

    async init() {
        this.setupCanvas();
        this.setupEventListeners();
        this.setupUI();
        await this.connectWebSocket();
        this.gameLoop();
    }

    setupCanvas() {
        this.canvas.width = window.innerWidth - 300;
        this.canvas.height = window.innerHeight;
        
        window.addEventListener('resize', () => {
            this.canvas.width = window.innerWidth - 300;
            this.canvas.height = window.innerHeight;
        });
    }

    setupEventListeners() {
        // Mouse movement for player
        this.canvas.addEventListener('mousemove', (e) => {
            if (this.playerFaction) {
                const rect = this.canvas.getBoundingClientRect();
                this.playerPosition.x = e.clientX - rect.left;
                this.playerPosition.y = e.clientY - rect.top;
                this.sendPlayerUpdate();
            }
        });

        // Click for extraction
        this.canvas.addEventListener('click', (e) => {
            if (this.playerFaction) {
                this.handleMapClick(e);
            }
        });

        // Faction selection
        document.querySelectorAll('.faction-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const factionId = parseInt(e.currentTarget.dataset.faction);
                this.selectFaction(factionId);
            });
        });

        // Map selection
        document.querySelectorAll('.map-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mapName = e.currentTarget.dataset.map;
                this.switchMap(mapName);
            });
        });

        // Chat
        const chatInput = document.getElementById('chatInput');
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.target.value.trim()) {
                this.sendChatMessage(e.target.value.trim());
                e.target.value = '';
            }
        });

        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            this.handleKeyPress(e);
        });
    }

    setupUI() {
        this.updateConnectionStatus('connecting');
        this.updateTerritorialDisplay();
    }

    async connectWebSocket() {
        try {
            this.websocket = new WebSocket('ws://127.0.0.1:8765');
            
            this.websocket.onopen = () => {
                this.updateConnectionStatus('connected');
                this.sendMessage({
                    action: 'join_game',
                    map: this.currentMap
                });
            };

            this.websocket.onmessage = (event) => {
                this.handleWebSocketMessage(JSON.parse(event.data));
            };

            this.websocket.onclose = () => {
                this.updateConnectionStatus('disconnected');
                // Attempt reconnection
                setTimeout(() => this.connectWebSocket(), 5000);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('disconnected');
            };

        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
            this.updateConnectionStatus('disconnected');
        }
    }

    selectFaction(factionId) {
        this.playerFaction = factionId;
        this.playerId = `player_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        document.getElementById('playerFaction').textContent = this.factions[factionId].name;
        document.getElementById('playerInfo').textContent = 
            `${this.factions[factionId].name} Operative`;

        // Highlight selected faction
        document.querySelectorAll('.faction-btn').forEach(btn => {
            btn.style.opacity = btn.dataset.faction == factionId ? '1' : '0.6';
        });

        // Send faction selection to server
        this.sendMessage({
            action: 'select_faction',
            player_id: this.playerId,
            faction_id: factionId,
            map: this.currentMap
        });

        // Position player in faction territory
        this.positionPlayerInFactionTerritory();
    }

    positionPlayerInFactionTerritory() {
        const map = this.maps[this.currentMap];
        const factionTerritories = map.territories.filter(t => t.faction === this.playerFaction);
        
        if (factionTerritories.length > 0) {
            const territory = factionTerritories[0];
            this.playerPosition.x = territory.x + (Math.random() - 0.5) * territory.radius;
            this.playerPosition.y = territory.y + (Math.random() - 0.5) * territory.radius;
        }
    }

    switchMap(mapName) {
        this.currentMap = mapName;
        
        // Update UI
        document.querySelectorAll('.map-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.map === mapName);
        });

        // Reposition player
        if (this.playerFaction) {
            this.positionPlayerInFactionTerritory();
        }

        // Notify server
        this.sendMessage({
            action: 'switch_map',
            player_id: this.playerId,
            map: mapName
        });

        this.updateTerritorialDisplay();
    }

    handleMapClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;

        // Check if clicking on extraction point
        const map = this.maps[this.currentMap];
        const extractionPoint = map.territories.find(t => {
            if (t.type === 'extraction') {
                const distance = Math.sqrt(Math.pow(clickX - t.x, 2) + Math.pow(clickY - t.y, 2));
                return distance <= t.radius;
            }
            return false;
        });

        if (extractionPoint) {
            this.startExtraction(extractionPoint);
        }
    }

    startExtraction(extractionPoint) {
        if (this.extractionActive) return;

        this.extractionActive = true;
        this.extractionTarget = extractionPoint;
        this.extractionProgress = 0;

        // Calculate extraction time based on territorial control
        const extractionTime = this.calculateExtractionTime(extractionPoint);
        
        document.getElementById('extractionProgress').style.display = 'block';
        
        // Send extraction start to server
        this.sendMessage({
            action: 'start_extraction',
            player_id: this.playerId,
            faction_id: this.playerFaction,
            territory_id: extractionPoint.id,
            extraction_time: extractionTime
        });

        this.addChatMessage('SYSTEM', `Starting extraction at ${extractionPoint.name}...`);
    }

    calculateExtractionTime(extractionPoint) {
        // Base extraction time: 30 seconds
        let extractionTime = 30000;

        // Faction control bonus
        if (extractionPoint.faction === this.playerFaction) {
            extractionTime -= 5000; // 5 second bonus
        }

        // Contested penalty
        if (extractionPoint.contested) {
            extractionTime += 10000; // 10 second penalty
        }

        return Math.max(extractionTime, 10000); // Minimum 10 seconds
    }

    handleWebSocketMessage(message) {
        switch (message.action) {
            case 'territorial_update':
                this.handleTerritorialUpdate(message);
                break;
            case 'player_update':
                this.handlePlayerUpdate(message);
                break;
            case 'extraction_progress':
                this.handleExtractionProgress(message);
                break;
            case 'extraction_complete':
                this.handleExtractionComplete(message);
                break;
            case 'chat_message':
                this.handleChatMessage(message);
                break;
            case 'game_state':
                this.handleGameState(message);
                break;
        }
    }

    handleTerritorialUpdate(message) {
        // Update territorial control data
        const territory = {
            id: message.territory_id,
            dominant_faction: message.dominant_faction,
            is_contested: message.is_contested,
            influence_percentages: message.influence_percentages
        };

        this.territories.set(message.territory_id, territory);
        this.updateTerritorialDisplay();
    }

    handlePlayerUpdate(message) {
        this.players.set(message.player_id, {
            faction: message.faction_id,
            position: message.position,
            status: message.status
        });
        
        document.getElementById('playerCount').textContent = this.players.size;
    }

    handleExtractionProgress(message) {
        if (message.player_id === this.playerId) {
            this.extractionProgress = message.progress;
            document.getElementById('extractionBar').style.width = `${this.extractionProgress}%`;
        }
    }

    handleExtractionComplete(message) {
        if (message.player_id === this.playerId) {
            this.extractionActive = false;
            this.extractionProgress = 0;
            document.getElementById('extractionProgress').style.display = 'none';
            
            if (message.success) {
                this.addChatMessage('SUCCESS', `Extraction completed! Gained ${message.territorial_influence} influence.`);
                
                // Update stats
                const currentExtractions = parseInt(document.getElementById('playerExtractions').textContent);
                document.getElementById('playerExtractions').textContent = currentExtractions + 1;
                
                const currentInfluence = parseInt(document.getElementById('playerInfluence').textContent);
                document.getElementById('playerInfluence').textContent = currentInfluence + message.territorial_influence;
            } else {
                this.addChatMessage('FAILURE', `Extraction failed: ${message.reason}`);
            }
        }
    }

    handleChatMessage(message) {
        this.addChatMessage(message.sender, message.content, message.faction_id);
    }

    handleGameState(message) {
        // Update overall game state
        if (message.territorial_balance) {
            this.validateTerritorialBalance(message.territorial_balance);
        }
    }

    validateTerritorialBalance(balance) {
        // Check if any faction exceeds 40% control (our validation target)
        for (const [factionId, percentage] of Object.entries(balance)) {
            if (percentage > 0.40) {
                this.addChatMessage('BALANCE WARNING', 
                    `${this.factions[factionId].name} controls ${(percentage * 100).toFixed(1)}% territory (exceeds 40% threshold)`);
            }
        }
    }

    sendMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }

    sendPlayerUpdate() {
        this.sendMessage({
            action: 'player_update',
            player_id: this.playerId,
            faction_id: this.playerFaction,
            position: this.playerPosition,
            map: this.currentMap
        });
    }

    sendChatMessage(content) {
        this.sendMessage({
            action: 'chat_message',
            player_id: this.playerId,
            faction_id: this.playerFaction,
            content: content
        });
    }

    addChatMessage(sender, content, factionId = null) {
        const chatMessages = document.getElementById('chatMessages');
        const messageElement = document.createElement('div');
        
        let color = '#ffffff';
        if (factionId && this.factions[factionId]) {
            color = this.factions[factionId].color;
        } else if (sender === 'SYSTEM') {
            color = '#ffaa00';
        } else if (sender === 'SUCCESS') {
            color = '#00ff00';
        } else if (sender === 'FAILURE') {
            color = '#ff0000';
        }

        messageElement.innerHTML = `<span style="color: ${color};">[${sender}]</span> ${content}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        statusElement.className = status;
    }

    updateTerritorialDisplay() {
        const territoryList = document.getElementById('territoryList');
        territoryList.innerHTML = '';

        const map = this.maps[this.currentMap];
        
        map.territories.forEach(territory => {
            const item = document.createElement('div');
            item.className = 'territory-item';
            
            let controlInfo = 'Neutral';
            let factionColor = '#666';

            if (territory.faction) {
                controlInfo = this.factions[territory.faction].shortName;
                factionColor = this.factions[territory.faction].color;
            } else if (territory.contested) {
                controlInfo = 'Contested';
                item.classList.add('territory-contested');
                factionColor = '#ff6600';
            }

            item.innerHTML = `
                <div style="color: ${factionColor};">
                    <strong>${territory.name}</strong>
                    <br>
                    <small>${controlInfo} • ${territory.type}</small>
                </div>
            `;
            
            territoryList.appendChild(item);
        });
    }

    handleKeyPress(e) {
        if (!this.playerFaction) return;

        const speed = 5;
        let moved = false;

        switch (e.key) {
            case 'w':
            case 'W':
            case 'ArrowUp':
                this.playerPosition.y = Math.max(0, this.playerPosition.y - speed);
                moved = true;
                break;
            case 's':
            case 'S':  
            case 'ArrowDown':
                this.playerPosition.y = Math.min(this.canvas.height, this.playerPosition.y + speed);
                moved = true;
                break;
            case 'a':
            case 'A':
            case 'ArrowLeft':
                this.playerPosition.x = Math.max(0, this.playerPosition.x - speed);
                moved = true;
                break;
            case 'd':
            case 'D':
            case 'ArrowRight':
                this.playerPosition.x = Math.min(this.canvas.width, this.playerPosition.x + speed);
                moved = true;
                break;
            case 'e':
            case 'E':
                // Quick extraction key
                this.attemptQuickExtraction();
                break;
        }

        if (moved) {
            this.sendPlayerUpdate();
        }
    }

    attemptQuickExtraction() {
        const map = this.maps[this.currentMap];
        const nearbyExtraction = map.territories.find(t => {
            if (t.type === 'extraction') {
                const distance = Math.sqrt(
                    Math.pow(this.playerPosition.x - t.x, 2) + 
                    Math.pow(this.playerPosition.y - t.y, 2)
                );
                return distance <= t.radius + 20; // 20 pixel buffer
            }
            return false;
        });

        if (nearbyExtraction) {
            this.startExtraction(nearbyExtraction);
        }
    }

    gameLoop() {
        this.render();
        requestAnimationFrame(() => this.gameLoop());
    }

    render() {
        // Clear canvas
        this.ctx.fillStyle = '#0a0a0a';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        const map = this.maps[this.currentMap];

        // Scale map to fit canvas
        const scaleX = this.canvas.width / map.size.width;
        const scaleY = this.canvas.height / map.size.height;
        const scale = Math.min(scaleX, scaleY, 1);

        this.ctx.save();
        this.ctx.scale(scale, scale);

        // Draw territories
        map.territories.forEach(territory => {
            this.drawTerritory(territory, scale);
        });

        // Draw other players
        this.players.forEach((player, playerId) => {
            if (playerId !== this.playerId) {
                this.drawPlayer(player, scale);
            }
        });

        // Draw current player
        if (this.playerFaction) {
            this.drawPlayer({
                faction: this.playerFaction,
                position: this.playerPosition
            }, scale, true);
        }

        this.ctx.restore();

        // Draw UI overlays
        this.drawMapInfo();
    }

    drawTerritory(territory, scale) {
        const x = territory.x;
        const y = territory.y;
        const radius = territory.radius;

        // Territory background
        this.ctx.globalAlpha = 0.3;
        this.ctx.fillStyle = territory.faction ? this.factions[territory.faction].color : '#333333';
        if (territory.contested) {
            this.ctx.fillStyle = '#ff6600';
        }
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, 0, Math.PI * 2);
        this.ctx.fill();

        // Territory border
        this.ctx.globalAlpha = 0.8;
        this.ctx.strokeStyle = territory.faction ? this.factions[territory.faction].color : '#666666';
        this.ctx.lineWidth = territory.type === 'extraction' ? 3 : 2;
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, 0, Math.PI * 2);
        this.ctx.stroke();

        // Territory name
        this.ctx.globalAlpha = 1;
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = '12px Courier New';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(territory.name, x, y - 5);

        // Territory type indicator
        this.ctx.font = '10px Courier New';
        this.ctx.fillText(territory.type.toUpperCase(), x, y + 8);

        // Extraction point indicator
        if (territory.type === 'extraction') {
            this.ctx.strokeStyle = '#ffff00';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius + 5, 0, Math.PI * 2);
            this.ctx.stroke();
        }
    }

    drawPlayer(player, scale, isCurrentPlayer = false) {
        const x = player.position.x;
        const y = player.position.y;
        const factionColor = this.factions[player.faction].color;

        // Player circle
        this.ctx.globalAlpha = isCurrentPlayer ? 1 : 0.8;
        this.ctx.fillStyle = factionColor;
        this.ctx.beginPath();
        this.ctx.arc(x, y, isCurrentPlayer ? 8 : 6, 0, Math.PI * 2);
        this.ctx.fill();

        // Player border
        this.ctx.strokeStyle = isCurrentPlayer ? '#ffffff' : factionColor;
        this.ctx.lineWidth = isCurrentPlayer ? 2 : 1;
        this.ctx.stroke();

        // Faction indicator
        if (isCurrentPlayer) {
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = '10px Courier New';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(this.factions[player.faction].shortName, x, y - 15);
        }

        this.ctx.globalAlpha = 1;
    }

    drawMapInfo() {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(10, this.canvas.height - 80, 300, 70);
        
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = '12px Courier New';
        this.ctx.textAlign = 'left';
        
        const map = this.maps[this.currentMap];
        this.ctx.fillText(`Map: ${map.name}`, 20, this.canvas.height - 60);
        this.ctx.fillText(`Size: ${map.size.width}m x ${map.size.height}m`, 20, this.canvas.height - 45);
        this.ctx.fillText(`Territories: ${map.territories.length}`, 20, this.canvas.height - 30);
        this.ctx.fillText('Controls: WASD/Arrow Keys, E to Extract', 20, this.canvas.height - 15);
    }
}

// Initialize game when page loads
window.addEventListener('DOMContentLoaded', () => {
    const game = new TerminalGroundsGame();
});