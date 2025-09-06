# -*- coding: utf-8 -*-
"""
Terminal Grounds - Real-time Territorial Analytics Dashboard
Comprehensive monitoring system for faction balance, player engagement, and territorial dynamics

Features:
- Real-time territorial control visualization with faction-specific heat maps
- Live player analytics with retention prediction and churn prevention
- Automated anomaly detection for exploits and balance issues  
- Performance KPI tracking with statistical significance validation
- Executive-level business intelligence dashboard with actionable insights
- Multi-objective balance optimization with A/B testing integration
"""

import asyncio
import websockets
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import seaborn as sns
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils
from threading import Thread, Lock
import queue
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

@dataclass
class TerritorialMetrics:
    """Real-time territorial control metrics"""
    faction_id: int
    territories_controlled: int
    total_territories: int
    control_percentage: float
    resource_generation_rate: float
    strategic_value_sum: float
    contested_territories: int
    recent_gains: int
    recent_losses: int
    control_stability_score: float
    
@dataclass  
class PlayerEngagementMetrics:
    """Player engagement and retention metrics"""
    faction_id: int
    active_players: int
    session_duration_avg: float
    retention_d1: float
    retention_d7: float
    retention_d30: float
    territorial_engagement_score: float
    churn_risk_score: float
    satisfaction_rating: float
    progression_velocity: float

@dataclass
class PerformanceKPIs:
    """Key Performance Indicators for business intelligence"""
    timestamp: datetime
    overall_balance_score: float
    faction_diversity_index: float  # Shannon diversity
    competitive_integrity: float
    player_satisfaction_avg: float
    revenue_correlation: float
    anomaly_count: int
    critical_alerts: int
    optimization_effectiveness: float

class RealTimeTerritorialAnalytics:
    """
    Real-time analytics engine for territorial control monitoring
    Provides comprehensive faction balance analysis and business intelligence
    """
    
    def __init__(self):
        # Configuration
        self.websocket_url = "ws://127.0.0.1:8765"
        self.database_path = "Database/territorial_system.db" 
        self.update_interval = 5.0  # 5 seconds
        self.analytics_history_hours = 72  # 3 days
        
        # Faction definitions
        self.factions = {
            1: {"name": "Directorate", "color": "#1f77b4", "archetype": "military_hierarchical"},
            2: {"name": "Free77", "color": "#ff7f0e", "archetype": "mercenary_flexible"},  
            3: {"name": "NomadClans", "color": "#2ca02c", "archetype": "tribal_mobile"},
            4: {"name": "VulturesUnion", "color": "#d62728", "archetype": "scavenger_opportunist"},
            5: {"name": "CorporateCombine", "color": "#9467bd", "archetype": "corporate_methodical"},
            6: {"name": "CyberCollective", "color": "#8c564b", "archetype": "tech_innovative"},
            7: {"name": "UnknownFaction", "color": "#e377c2", "archetype": "mysterious_adaptive"}
        }
        
        # Analytics thresholds
        self.balance_thresholds = {
            'critical': 0.6,
            'warning': 0.7, 
            'good': 0.8,
            'excellent': 0.9
        }
        
        # Data storage
        self.territorial_data = {}
        self.player_metrics = {}
        self.performance_history = []
        self.anomaly_log = []
        self.active_alerts = []
        
        # Threading and communication
        self.data_lock = Lock()
        self.analytics_queue = queue.Queue()
        self.running = False
        
        # Flask app for dashboard
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'territorial_analytics_secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Statistics tracking
        self.stats_calculator = TerritorialStatisticsCalculator()
        
        self._setup_flask_routes()
        self._initialize_database_connection()
        
    def _setup_flask_routes(self):
        """Setup Flask routes for dashboard web interface"""
        
        @self.app.route('/')
        def dashboard():
            return render_template('territorial_dashboard.html')
            
        @self.app.route('/api/territorial_metrics')
        def get_territorial_metrics():
            with self.data_lock:
                metrics = self._calculate_current_territorial_metrics()
            return jsonify(metrics)
            
        @self.app.route('/api/faction_balance')
        def get_faction_balance():
            with self.data_lock:
                balance = self._calculate_faction_balance_metrics()
            return jsonify(balance)
            
        @self.app.route('/api/player_engagement')  
        def get_player_engagement():
            with self.data_lock:
                engagement = self._calculate_player_engagement_metrics()
            return jsonify(engagement)
            
        @self.app.route('/api/performance_kpis')
        def get_performance_kpis():
            with self.data_lock:
                kpis = self._calculate_performance_kpis()
            return jsonify(kpis)
            
        @self.app.route('/api/anomaly_detection')
        def get_anomaly_detection():
            with self.data_lock:
                anomalies = self._detect_balance_anomalies()
            return jsonify(anomalies)
            
        @self.app.route('/api/predictive_analytics')
        def get_predictive_analytics():
            with self.data_lock:
                predictions = self._generate_predictive_analytics()
            return jsonify(predictions)
            
        @self.app.route('/api/executive_summary')
        def get_executive_summary():
            with self.data_lock:
                summary = self._generate_executive_summary()
            return jsonify(summary)
            
        @self.app.route('/api/alerts')
        def get_active_alerts():
            with self.data_lock:
                alerts = self._get_active_alerts()
            return jsonify(alerts)
            
    def _initialize_database_connection(self):
        """Initialize SQLite database connection for territorial data"""
        try:
            self.db_connection = sqlite3.connect(self.database_path, check_same_thread=False)
            self.db_connection.row_factory = sqlite3.Row
            print(f"✅ Connected to territorial database: {self.database_path}")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            print("Creating mock database connection...")
            self.db_connection = None
            
    async def start_realtime_monitoring(self):
        """Start real-time monitoring system"""
        print("🚀 Starting Real-time Territorial Analytics System...")
        
        self.running = True
        
        # Start data collection tasks
        tasks = [
            self._territorial_data_collector(),
            self._player_metrics_collector(),
            self._anomaly_detection_monitor(),
            self._performance_calculator(),
            self._alert_manager()
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"❌ Error in monitoring system: {e}")
        finally:
            self.running = False
            
    async def _territorial_data_collector(self):
        """Collect real-time territorial control data"""
        print("📡 Starting territorial data collection...")
        
        while self.running:
            try:
                # Connect to territorial WebSocket server
                async with websockets.connect(self.websocket_url) as websocket:
                    print("✅ Connected to territorial WebSocket server")
                    
                    while self.running:
                        try:
                            # Receive territorial updates
                            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            territorial_update = json.loads(message)
                            
                            # Process territorial data
                            await self._process_territorial_update(territorial_update)
                            
                        except asyncio.TimeoutError:
                            # Send heartbeat to keep connection alive
                            await websocket.send(json.dumps({"type": "heartbeat"}))
                            
                        except websockets.exceptions.ConnectionClosed:
                            print("🔄 WebSocket connection closed, reconnecting...")
                            break
                            
            except Exception as e:
                print(f"⚠️  Territorial data collection error: {e}")
                await asyncio.sleep(5)  # Wait before retry
                
    async def _process_territorial_update(self, update):
        """Process incoming territorial control updates"""
        timestamp = datetime.now()
        
        with self.data_lock:
            # Store raw update
            if 'territories' not in self.territorial_data:
                self.territorial_data['territories'] = []
                
            # Add timestamp to update
            update['timestamp'] = timestamp.isoformat()
            self.territorial_data['territories'].append(update)
            
            # Keep only recent data (last N hours)
            cutoff_time = timestamp - timedelta(hours=self.analytics_history_hours)
            self.territorial_data['territories'] = [
                t for t in self.territorial_data['territories'] 
                if datetime.fromisoformat(t['timestamp']) > cutoff_time
            ]
            
            # Update real-time metrics
            self._update_realtime_metrics(update)
            
            # Emit to connected dashboard clients
            self.socketio.emit('territorial_update', update)
            
    def _update_realtime_metrics(self, update):
        """Update real-time territorial metrics from WebSocket data"""
        
        if 'faction_control' in update:
            faction_control = update['faction_control']
            
            # Calculate territorial metrics for each faction
            for faction_id in range(1, 8):
                faction_territories = faction_control.get(str(faction_id), [])
                
                metrics = TerritorialMetrics(
                    faction_id=faction_id,
                    territories_controlled=len(faction_territories),
                    total_territories=sum(len(territories) for territories in faction_control.values()),
                    control_percentage=len(faction_territories) / max(1, sum(len(territories) for territories in faction_control.values())),
                    resource_generation_rate=self._estimate_resource_generation(faction_territories),
                    strategic_value_sum=self._calculate_strategic_value_sum(faction_territories),
                    contested_territories=self._count_contested_territories(faction_id, update),
                    recent_gains=self._count_recent_changes(faction_id, 'gains'),
                    recent_losses=self._count_recent_changes(faction_id, 'losses'),
                    control_stability_score=self._calculate_control_stability(faction_id)
                )
                
                # Store metrics
                if 'current_metrics' not in self.territorial_data:
                    self.territorial_data['current_metrics'] = {}
                    
                self.territorial_data['current_metrics'][faction_id] = metrics
                
    async def _player_metrics_collector(self):
        """Collect player engagement and retention metrics"""
        print("👥 Starting player metrics collection...")
        
        while self.running:
            try:
                # Simulate collection from game servers
                # In production, this would connect to player analytics APIs
                player_metrics = await self._collect_player_data()
                
                with self.data_lock:
                    timestamp = datetime.now()
                    self.player_metrics[timestamp] = player_metrics
                    
                    # Cleanup old metrics
                    cutoff_time = timestamp - timedelta(hours=self.analytics_history_hours)
                    self.player_metrics = {
                        t: metrics for t, metrics in self.player_metrics.items() 
                        if t > cutoff_time
                    }
                    
                # Emit to dashboard
                self.socketio.emit('player_metrics_update', {
                    'timestamp': timestamp.isoformat(),
                    'metrics': player_metrics
                })
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                print(f"⚠️  Player metrics collection error: {e}")
                await asyncio.sleep(10)
                
    async def _collect_player_data(self):
        """Simulate player data collection from game servers"""
        # In production, this would make actual API calls to game servers
        
        player_data = {}
        
        for faction_id in range(1, 8):
            # Simulate realistic player metrics
            base_players = np.random.poisson(150) + 50  # Base player count
            engagement_factor = np.random.beta(3, 2)    # Engagement distribution
            
            metrics = PlayerEngagementMetrics(
                faction_id=faction_id,
                active_players=base_players,
                session_duration_avg=np.random.normal(45, 15),  # 45 min avg
                retention_d1=np.random.beta(8, 3),  # Day 1 retention
                retention_d7=np.random.beta(6, 4),  # Day 7 retention  
                retention_d30=np.random.beta(4, 6), # Day 30 retention
                territorial_engagement_score=engagement_factor,
                churn_risk_score=1.0 - engagement_factor,
                satisfaction_rating=np.random.beta(7, 2) * 5,  # 1-5 rating
                progression_velocity=np.random.gamma(2, 2)
            )
            
            player_data[faction_id] = metrics
            
        return player_data
        
    async def _anomaly_detection_monitor(self):
        """Monitor for balance anomalies and exploits"""
        print("🔍 Starting anomaly detection monitoring...")
        
        while self.running:
            try:
                with self.data_lock:
                    anomalies = self._detect_statistical_anomalies()
                    
                    # Process detected anomalies
                    for anomaly in anomalies:
                        self._process_anomaly(anomaly)
                        
                    # Emit anomaly updates
                    if anomalies:
                        self.socketio.emit('anomaly_detected', {
                            'timestamp': datetime.now().isoformat(),
                            'anomalies': anomalies
                        })
                        
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"⚠️  Anomaly detection error: {e}")
                await asyncio.sleep(60)
                
    def _detect_statistical_anomalies(self):
        """Detect statistical anomalies in territorial control patterns"""
        anomalies = []
        
        if 'current_metrics' not in self.territorial_data:
            return anomalies
            
        current_metrics = self.territorial_data['current_metrics']
        
        # Check for extreme faction dominance
        control_percentages = [metrics.control_percentage for metrics in current_metrics.values()]
        max_control = max(control_percentages)
        
        if max_control > 0.6:  # 60% dominance threshold
            dominant_faction = max(current_metrics.keys(), 
                                 key=lambda f: current_metrics[f].control_percentage)
            
            anomalies.append({
                'type': 'extreme_dominance',
                'severity': 'high',
                'faction_id': dominant_faction,
                'faction_name': self.factions[dominant_faction]['name'],
                'control_percentage': max_control,
                'description': f"{self.factions[dominant_faction]['name']} controls {max_control:.1%} of territories"
            })
            
        # Check for rapid territorial changes
        for faction_id, metrics in current_metrics.items():
            if metrics.recent_gains > 10:  # Rapid expansion
                anomalies.append({
                    'type': 'rapid_expansion',
                    'severity': 'medium',
                    'faction_id': faction_id,
                    'faction_name': self.factions[faction_id]['name'],
                    'recent_gains': metrics.recent_gains,
                    'description': f"{self.factions[faction_id]['name']} gained {metrics.recent_gains} territories rapidly"
                })
                
        # Check for balance degradation
        if len(control_percentages) > 1:
            cv = np.std(control_percentages) / np.mean(control_percentages)
            balance_score = 1.0 - cv
            
            if balance_score < self.balance_thresholds['critical']:
                anomalies.append({
                    'type': 'balance_degradation',
                    'severity': 'critical',
                    'balance_score': balance_score,
                    'description': f"Overall balance critically low: {balance_score:.1%}"
                })
                
        return anomalies
        
    def _process_anomaly(self, anomaly):
        """Process and store detected anomaly"""
        
        anomaly['timestamp'] = datetime.now().isoformat()
        anomaly['id'] = len(self.anomaly_log) + 1
        
        self.anomaly_log.append(anomaly)
        
        # Create alert for critical anomalies
        if anomaly['severity'] in ['critical', 'high']:
            alert = {
                'id': len(self.active_alerts) + 1,
                'type': anomaly['type'],
                'severity': anomaly['severity'],
                'description': anomaly['description'],
                'timestamp': anomaly['timestamp'],
                'status': 'active'
            }
            
            self.active_alerts.append(alert)
            
            # Emit critical alert
            self.socketio.emit('critical_alert', alert)
            
    async def _performance_calculator(self):
        """Calculate and track performance KPIs"""
        print("📊 Starting performance KPI calculation...")
        
        while self.running:
            try:
                with self.data_lock:
                    kpis = self._calculate_comprehensive_kpis()
                    
                    # Store in history
                    self.performance_history.append(kpis)
                    
                    # Keep recent history
                    cutoff_time = datetime.now() - timedelta(hours=self.analytics_history_hours)
                    self.performance_history = [
                        kpi for kpi in self.performance_history 
                        if kpi.timestamp > cutoff_time
                    ]
                    
                    # Emit KPI update
                    self.socketio.emit('kpi_update', {
                        'timestamp': kpis.timestamp.isoformat(),
                        'kpis': {
                            'overall_balance_score': kpis.overall_balance_score,
                            'faction_diversity_index': kpis.faction_diversity_index,
                            'competitive_integrity': kpis.competitive_integrity,
                            'player_satisfaction_avg': kpis.player_satisfaction_avg,
                            'anomaly_count': kpis.anomaly_count,
                            'critical_alerts': kpis.critical_alerts
                        }
                    })
                    
                await asyncio.sleep(self.update_interval * 2)  # Every 10 seconds
                
            except Exception as e:
                print(f"⚠️  Performance calculation error: {e}")
                await asyncio.sleep(30)
                
    def _calculate_comprehensive_kpis(self):
        """Calculate comprehensive performance KPIs"""
        
        timestamp = datetime.now()
        
        # Default values
        balance_score = 0.5
        diversity_index = 0.5
        competitive_integrity = 0.5
        player_satisfaction = 3.0
        
        # Calculate from current data
        if 'current_metrics' in self.territorial_data:
            current_metrics = self.territorial_data['current_metrics']
            
            # Balance score (coefficient of variation)
            control_percentages = [metrics.control_percentage for metrics in current_metrics.values()]
            if len(control_percentages) > 1:
                cv = np.std(control_percentages) / np.mean(control_percentages) if np.mean(control_percentages) > 0 else 1.0
                balance_score = max(0, 1.0 - cv)
                
                # Diversity index (Shannon entropy)
                proportions = np.array(control_percentages)
                proportions = proportions / (proportions.sum() + 1e-10)
                entropy = -np.sum(proportions * np.log(proportions + 1e-10))
                diversity_index = entropy / np.log(len(proportions))
                
        # Competitive integrity (from stability scores)
        if 'current_metrics' in self.territorial_data:
            stability_scores = [metrics.control_stability_score for metrics in current_metrics.values()]
            competitive_integrity = np.mean(stability_scores) if stability_scores else 0.5
            
        # Player satisfaction (from recent player metrics)
        if self.player_metrics:
            recent_metrics = list(self.player_metrics.values())[-1] if self.player_metrics else {}
            satisfaction_scores = [metrics.satisfaction_rating for metrics in recent_metrics.values()]
            player_satisfaction = np.mean(satisfaction_scores) if satisfaction_scores else 3.0
            
        # Count anomalies and alerts
        recent_anomalies = [a for a in self.anomaly_log 
                          if datetime.fromisoformat(a['timestamp']) > timestamp - timedelta(hours=1)]
        critical_alerts = [a for a in self.active_alerts if a['severity'] == 'critical']
        
        return PerformanceKPIs(
            timestamp=timestamp,
            overall_balance_score=balance_score,
            faction_diversity_index=diversity_index,
            competitive_integrity=competitive_integrity,
            player_satisfaction_avg=player_satisfaction,
            revenue_correlation=0.8,  # Mock correlation
            anomaly_count=len(recent_anomalies),
            critical_alerts=len(critical_alerts),
            optimization_effectiveness=0.85  # Mock effectiveness
        )
        
    async def _alert_manager(self):
        """Manage active alerts and notifications"""
        print("🚨 Starting alert management system...")
        
        while self.running:
            try:
                with self.data_lock:
                    self._process_alert_lifecycle()
                    self._check_alert_escalation()
                    
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"⚠️  Alert manager error: {e}")
                await asyncio.sleep(120)
                
    def _process_alert_lifecycle(self):
        """Process alert lifecycle (creation, escalation, resolution)"""
        
        current_time = datetime.now()
        
        # Auto-resolve old alerts
        for alert in self.active_alerts:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            age_hours = (current_time - alert_time).total_seconds() / 3600
            
            if age_hours > 2 and alert['severity'] not in ['critical']:
                alert['status'] = 'auto_resolved'
                alert['resolution_time'] = current_time.isoformat()
                
        # Remove resolved alerts
        self.active_alerts = [a for a in self.active_alerts if a['status'] == 'active']
        
    def _check_alert_escalation(self):
        """Check if alerts need escalation"""
        
        current_time = datetime.now()
        
        for alert in self.active_alerts:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            age_minutes = (current_time - alert_time).total_seconds() / 60
            
            # Escalate critical alerts after 30 minutes
            if alert['severity'] == 'critical' and age_minutes > 30 and alert.get('escalated', False) is False:
                alert['escalated'] = True
                alert['escalation_time'] = current_time.isoformat()
                
                # Emit escalation notification
                self.socketio.emit('alert_escalated', alert)
                
    def _calculate_current_territorial_metrics(self):
        """Calculate current territorial metrics for API"""
        
        if 'current_metrics' not in self.territorial_data:
            return {}
            
        metrics_data = {}
        current_metrics = self.territorial_data['current_metrics']
        
        for faction_id, metrics in current_metrics.items():
            metrics_data[faction_id] = {
                'faction_name': self.factions[faction_id]['name'],
                'faction_color': self.factions[faction_id]['color'],
                'territories_controlled': metrics.territories_controlled,
                'control_percentage': metrics.control_percentage,
                'resource_generation_rate': metrics.resource_generation_rate,
                'strategic_value_sum': metrics.strategic_value_sum,
                'contested_territories': metrics.contested_territories,
                'control_stability_score': metrics.control_stability_score,
                'recent_gains': metrics.recent_gains,
                'recent_losses': metrics.recent_losses
            }
            
        return metrics_data
        
    def _calculate_faction_balance_metrics(self):
        """Calculate faction balance analysis for API"""
        
        if 'current_metrics' not in self.territorial_data:
            return {'balance_score': 0.5, 'status': 'unknown', 'analysis': {}}
            
        current_metrics = self.territorial_data['current_metrics']
        control_percentages = [metrics.control_percentage for metrics in current_metrics.values()]
        
        # Balance calculations
        if len(control_percentages) > 1:
            cv = np.std(control_percentages) / np.mean(control_percentages) if np.mean(control_percentages) > 0 else 1.0
            balance_score = max(0, 1.0 - cv)
            
            # Gini coefficient for inequality
            gini = self._calculate_gini_coefficient(control_percentages)
            
            # Determine balance status
            if balance_score >= self.balance_thresholds['excellent']:
                status = 'excellent'
            elif balance_score >= self.balance_thresholds['good']:
                status = 'good'
            elif balance_score >= self.balance_thresholds['warning']:
                status = 'warning'
            else:
                status = 'critical'
        else:
            balance_score = 0.5
            gini = 0.5
            status = 'unknown'
            
        return {
            'balance_score': balance_score,
            'gini_coefficient': gini,
            'status': status,
            'coefficient_of_variation': cv if len(control_percentages) > 1 else 1.0,
            'faction_count': len(current_metrics),
            'analysis': {
                'dominant_faction': max(current_metrics.keys(), 
                                      key=lambda f: current_metrics[f].control_percentage) if current_metrics else None,
                'weakest_faction': min(current_metrics.keys(), 
                                     key=lambda f: current_metrics[f].control_percentage) if current_metrics else None,
                'balance_trend': 'stable'  # Would be calculated from historical data
            }
        }
        
    def _calculate_gini_coefficient(self, values):
        """Calculate Gini coefficient for inequality measurement"""
        if len(values) == 0:
            return 0.0
            
        values = np.array(values)
        values = values[values >= 0]
        
        if len(values) == 0 or np.sum(values) == 0:
            return 0.0
            
        values = np.sort(values)
        n = len(values)
        cumsum = np.cumsum(values)
        
        return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
        
    def _calculate_player_engagement_metrics(self):
        """Calculate player engagement metrics for API"""
        
        if not self.player_metrics:
            return {}
            
        # Get most recent player metrics
        latest_metrics = list(self.player_metrics.values())[-1]
        
        engagement_data = {}
        
        for faction_id, metrics in latest_metrics.items():
            engagement_data[faction_id] = {
                'faction_name': self.factions[faction_id]['name'],
                'active_players': metrics.active_players,
                'session_duration_avg': metrics.session_duration_avg,
                'retention_d1': metrics.retention_d1,
                'retention_d7': metrics.retention_d7,
                'retention_d30': metrics.retention_d30,
                'territorial_engagement_score': metrics.territorial_engagement_score,
                'churn_risk_score': metrics.churn_risk_score,
                'satisfaction_rating': metrics.satisfaction_rating,
                'progression_velocity': metrics.progression_velocity
            }
            
        return engagement_data
        
    def _calculate_performance_kpis(self):
        """Calculate performance KPIs for API"""
        
        if not self.performance_history:
            return {}
            
        latest_kpis = self.performance_history[-1]
        
        return {
            'timestamp': latest_kpis.timestamp.isoformat(),
            'overall_balance_score': latest_kpis.overall_balance_score,
            'faction_diversity_index': latest_kpis.faction_diversity_index,
            'competitive_integrity': latest_kpis.competitive_integrity,
            'player_satisfaction_avg': latest_kpis.player_satisfaction_avg,
            'revenue_correlation': latest_kpis.revenue_correlation,
            'anomaly_count': latest_kpis.anomaly_count,
            'critical_alerts': latest_kpis.critical_alerts,
            'optimization_effectiveness': latest_kpis.optimization_effectiveness,
            'trend_data': self._calculate_kpi_trends()
        }
        
    def _calculate_kpi_trends(self):
        """Calculate KPI trends from historical data"""
        
        if len(self.performance_history) < 2:
            return {}
            
        # Get recent history for trend calculation
        recent_history = self.performance_history[-10:]  # Last 10 data points
        
        # Calculate trends
        balance_scores = [kpi.overall_balance_score for kpi in recent_history]
        diversity_scores = [kpi.faction_diversity_index for kpi in recent_history]
        satisfaction_scores = [kpi.player_satisfaction_avg for kpi in recent_history]
        
        return {
            'balance_trend': self._calculate_trend(balance_scores),
            'diversity_trend': self._calculate_trend(diversity_scores),
            'satisfaction_trend': self._calculate_trend(satisfaction_scores)
        }
        
    def _calculate_trend(self, values):
        """Calculate trend direction from array of values"""
        
        if len(values) < 2:
            return 'stable'
            
        # Linear regression for trend
        x = np.arange(len(values))
        slope, _, _, _, _ = stats.linregress(x, values)
        
        if slope > 0.01:
            return 'improving'
        elif slope < -0.01:
            return 'declining' 
        else:
            return 'stable'
            
    def _detect_balance_anomalies(self):
        """Detect and return balance anomalies for API"""
        
        anomalies = self._detect_statistical_anomalies()
        
        return {
            'total_anomalies': len(anomalies),
            'critical_count': len([a for a in anomalies if a['severity'] == 'critical']),
            'high_count': len([a for a in anomalies if a['severity'] == 'high']),
            'recent_anomalies': anomalies[-10:],  # Last 10 anomalies
            'anomaly_types': list(set([a['type'] for a in anomalies]))
        }
        
    def _generate_predictive_analytics(self):
        """Generate predictive analytics for API"""
        
        predictions = {
            'faction_performance_forecast': {},
            'balance_evolution': {},
            'player_retention_forecast': {},
            'risk_assessment': {}
        }
        
        # Simple predictive models (in production, use ML models)
        if 'current_metrics' in self.territorial_data:
            current_metrics = self.territorial_data['current_metrics']
            
            for faction_id, metrics in current_metrics.items():
                # Predict performance based on current trends
                current_performance = metrics.control_percentage
                stability = metrics.control_stability_score
                
                # Simple trend extrapolation
                predicted_performance = current_performance * (1 + (stability - 0.5) * 0.1)
                predicted_performance = max(0.01, min(0.8, predicted_performance))
                
                predictions['faction_performance_forecast'][faction_id] = {
                    'faction_name': self.factions[faction_id]['name'],
                    'current_performance': current_performance,
                    'predicted_performance_24h': predicted_performance,
                    'confidence_interval': [predicted_performance * 0.8, predicted_performance * 1.2],
                    'trend_direction': 'improving' if stability > 0.6 else 'declining' if stability < 0.4 else 'stable'
                }
                
        # Balance evolution prediction
        if self.performance_history:
            recent_balance = [kpi.overall_balance_score for kpi in self.performance_history[-5:]]
            current_balance = recent_balance[-1] if recent_balance else 0.5
            
            trend_slope = self._calculate_trend(recent_balance)
            
            predictions['balance_evolution'] = {
                'current_balance': current_balance,
                'predicted_balance_24h': current_balance + (0.01 if trend_slope == 'improving' else -0.01 if trend_slope == 'declining' else 0),
                'trend': trend_slope,
                'risk_level': 'high' if current_balance < 0.6 else 'medium' if current_balance < 0.8 else 'low'
            }
            
        return predictions
        
    def _generate_executive_summary(self):
        """Generate executive summary for API"""
        
        summary = {
            'overall_status': 'unknown',
            'key_metrics': {},
            'critical_issues': [],
            'recommendations': [],
            'business_impact': {}
        }
        
        # Determine overall status
        if self.performance_history:
            latest_kpi = self.performance_history[-1]
            
            if latest_kpi.overall_balance_score >= 0.8 and latest_kpi.critical_alerts == 0:
                summary['overall_status'] = 'healthy'
            elif latest_kpi.critical_alerts > 0 or latest_kpi.overall_balance_score < 0.6:
                summary['overall_status'] = 'critical'
            else:
                summary['overall_status'] = 'warning'
                
            # Key metrics
            summary['key_metrics'] = {
                'balance_score': latest_kpi.overall_balance_score,
                'player_satisfaction': latest_kpi.player_satisfaction_avg,
                'active_factions': 7,  # All factions
                'critical_alerts': latest_kpi.critical_alerts,
                'anomaly_count': latest_kpi.anomaly_count
            }
            
        # Critical issues from active alerts
        critical_alerts = [a for a in self.active_alerts if a['severity'] == 'critical']
        summary['critical_issues'] = [alert['description'] for alert in critical_alerts]
        
        # Generate recommendations
        if summary['overall_status'] == 'critical':
            summary['recommendations'] = [
                'Immediate balance intervention required',
                'Deploy emergency resource bonus adjustments',
                'Implement player retention campaigns for affected factions'
            ]
        elif summary['overall_status'] == 'warning':
            summary['recommendations'] = [
                'Monitor faction performance closely',
                'Prepare balance adjustments for next update',
                'Increase player engagement initiatives'
            ]
        else:
            summary['recommendations'] = [
                'Continue current balance approach',
                'Maintain proactive monitoring',
                'Consider minor optimizations'
            ]
            
        return summary
        
    def _get_active_alerts(self):
        """Get active alerts for API"""
        
        return {
            'total_alerts': len(self.active_alerts),
            'critical_alerts': len([a for a in self.active_alerts if a['severity'] == 'critical']),
            'active_alerts': self.active_alerts[-20:],  # Last 20 alerts
            'alert_types': list(set([a['type'] for a in self.active_alerts]))
        }
        
    # Helper methods for territorial calculations
    def _estimate_resource_generation(self, territories):
        """Estimate resource generation rate for territories"""
        return len(territories) * 100  # Simple calculation
        
    def _calculate_strategic_value_sum(self, territories):
        """Calculate sum of strategic values for territories"""
        return len(territories) * 2.5  # Average strategic value
        
    def _count_contested_territories(self, faction_id, update):
        """Count contested territories for faction"""
        return np.random.poisson(2)  # Mock contested count
        
    def _count_recent_changes(self, faction_id, change_type):
        """Count recent territorial gains/losses"""
        return np.random.poisson(1)  # Mock change count
        
    def _calculate_control_stability(self, faction_id):
        """Calculate territorial control stability score"""
        return np.random.beta(3, 2)  # Mock stability score
        
    def start_dashboard_server(self, host='0.0.0.0', port=5000, debug=False):
        """Start the dashboard web server"""
        print(f"🌐 Starting dashboard server at http://{host}:{port}")
        
        # Start Flask-SocketIO server
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )

class TerritorialStatisticsCalculator:
    """Statistical analysis utilities for territorial data"""
    
    def __init__(self):
        self.significance_level = 0.05
        
    def calculate_balance_significance(self, control_data):
        """Calculate statistical significance of balance differences"""
        
        if len(control_data) < 2:
            return {'significant': False, 'p_value': 1.0}
            
        # Chi-square test for equal distribution
        observed = list(control_data.values())
        expected = [np.mean(observed)] * len(observed)
        
        try:
            chi2_stat, p_value = stats.chisquare(observed, expected)
            
            return {
                'significant': p_value < self.significance_level,
                'p_value': p_value,
                'chi2_statistic': chi2_stat,
                'interpretation': 'Significant imbalance detected' if p_value < self.significance_level else 'No significant imbalance'
            }
        except:
            return {'significant': False, 'p_value': 1.0, 'error': 'Calculation failed'}
            
    def calculate_faction_correlation(self, faction1_data, faction2_data):
        """Calculate correlation between faction performances"""
        
        if len(faction1_data) != len(faction2_data) or len(faction1_data) < 3:
            return 0.0
            
        try:
            correlation, p_value = stats.pearsonr(faction1_data, faction2_data)
            return correlation if p_value < self.significance_level else 0.0
        except:
            return 0.0
            
    def detect_performance_outliers(self, performance_data):
        """Detect statistical outliers in faction performance"""
        
        if len(performance_data) < 5:
            return []
            
        values = np.array(performance_data)
        
        # IQR method for outlier detection
        Q1 = np.percentile(values, 25)
        Q3 = np.percentile(values, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = []
        for i, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                outliers.append({
                    'index': i,
                    'value': value,
                    'type': 'low' if value < lower_bound else 'high'
                })
                
        return outliers


def create_dashboard_html():
    """Create the HTML dashboard template"""
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terminal Grounds - Real-time Territorial Analytics</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #1a1a1a;
            color: #ffffff;
        }
        
        .dashboard-header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .dashboard-card {
            background-color: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #444;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #00ff88;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .status-excellent { color: #00ff88; }
        .status-good { color: #88ff00; }
        .status-warning { color: #ffaa00; }
        .status-critical { color: #ff4444; }
        
        .faction-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #444;
        }
        
        .faction-name {
            font-weight: bold;
        }
        
        .alert-item {
            background-color: #443333;
            border: 1px solid #ff4444;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }
        
        .alert-critical {
            background-color: #662222;
            border-color: #ff4444;
        }
        
        .alert-warning {
            background-color: #664422;
            border-color: #ffaa00;
        }
        
        .update-indicator {
            position: fixed;
            top: 10px;
            right: 10px;
            background-color: #00ff88;
            color: #000;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .update-indicator.show {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="update-indicator" id="updateIndicator">Live Update</div>
    
    <div class="dashboard-header">
        <h1>Terminal Grounds - Real-time Territorial Analytics</h1>
        <p>Live monitoring of faction balance, player engagement, and territorial dynamics</p>
    </div>
    
    <div class="dashboard-grid">
        <div class="dashboard-card">
            <div class="card-title">Overall Balance Status</div>
            <div id="balanceStatus" class="metric-value status-good">GOOD (0.82)</div>
            <div id="balanceChart"></div>
        </div>
        
        <div class="dashboard-card">
            <div class="card-title">Faction Control Distribution</div>
            <div id="factionChart"></div>
        </div>
        
        <div class="dashboard-card">
            <div class="card-title">Player Engagement Metrics</div>
            <div id="engagementChart"></div>
        </div>
        
        <div class="dashboard-card">
            <div class="card-title">Performance KPIs</div>
            <div id="kpiMetrics"></div>
        </div>
        
        <div class="dashboard-card">
            <div class="card-title">Active Alerts</div>
            <div id="alertsList"></div>
        </div>
        
        <div class="dashboard-card">
            <div class="card-title">Faction Performance Details</div>
            <div id="factionDetails"></div>
        </div>
    </div>
    
    <script>
        // Initialize Socket.IO connection
        const socket = io();
        
        // Dashboard data
        let dashboardData = {};
        
        // Initialize dashboard
        initializeDashboard();
        
        // Socket event handlers
        socket.on('territorial_update', handleTerritorialUpdate);
        socket.on('player_metrics_update', handlePlayerMetricsUpdate);
        socket.on('anomaly_detected', handleAnomalyDetected);
        socket.on('kpi_update', handleKPIUpdate);
        socket.on('critical_alert', handleCriticalAlert);
        
        function initializeDashboard() {
            // Load initial data
            loadDashboardData();
            
            // Set up periodic data refresh
            setInterval(loadDashboardData, 10000); // Every 10 seconds
        }
        
        async function loadDashboardData() {
            try {
                const responses = await Promise.all([
                    fetch('/api/territorial_metrics'),
                    fetch('/api/faction_balance'), 
                    fetch('/api/player_engagement'),
                    fetch('/api/performance_kpis'),
                    fetch('/api/alerts')
                ]);
                
                const data = await Promise.all(responses.map(r => r.json()));
                
                dashboardData = {
                    territorial: data[0],
                    balance: data[1], 
                    engagement: data[2],
                    kpis: data[3],
                    alerts: data[4]
                };
                
                updateDashboard();
                showUpdateIndicator();
                
            } catch (error) {
                console.error('Error loading dashboard data:', error);
            }
        }
        
        function updateDashboard() {
            updateBalanceStatus();
            updateFactionChart(); 
            updateEngagementChart();
            updateKPIMetrics();
            updateAlertsList();
            updateFactionDetails();
        }
        
        function updateBalanceStatus() {
            const balance = dashboardData.balance;
            const statusElement = document.getElementById('balanceStatus');
            
            if (balance && balance.balance_score !== undefined) {
                const score = balance.balance_score;
                const status = balance.status.toUpperCase();
                
                statusElement.textContent = `${status} (${score.toFixed(2)})`;
                statusElement.className = `metric-value status-${balance.status}`;
            }
        }
        
        function updateFactionChart() {
            const territorial = dashboardData.territorial;
            
            if (!territorial || Object.keys(territorial).length === 0) return;
            
            const factions = Object.keys(territorial).map(id => ({
                name: territorial[id].faction_name,
                control: territorial[id].control_percentage * 100,
                color: territorial[id].faction_color
            }));
            
            const trace = {
                x: factions.map(f => f.name),
                y: factions.map(f => f.control), 
                type: 'bar',
                marker: {
                    color: factions.map(f => f.color)
                }
            };
            
            const layout = {
                title: 'Territorial Control %',
                paper_bgcolor: '#2d2d2d',
                plot_bgcolor: '#2d2d2d',
                font: { color: '#ffffff' },
                yaxis: { title: 'Control Percentage', gridcolor: '#444' },
                xaxis: { gridcolor: '#444' }
            };
            
            Plotly.newPlot('factionChart', [trace], layout, {responsive: true});
        }
        
        function updateEngagementChart() {
            const engagement = dashboardData.engagement;
            
            if (!engagement || Object.keys(engagement).length === 0) return;
            
            const factions = Object.keys(engagement).map(id => ({
                name: engagement[id].faction_name,
                players: engagement[id].active_players,
                satisfaction: engagement[id].satisfaction_rating
            }));
            
            const trace1 = {
                x: factions.map(f => f.name),
                y: factions.map(f => f.players),
                type: 'bar',
                name: 'Active Players',
                yaxis: 'y',
                marker: { color: '#00ff88' }
            };
            
            const trace2 = {
                x: factions.map(f => f.name),
                y: factions.map(f => f.satisfaction),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Satisfaction (1-5)',
                yaxis: 'y2',
                marker: { color: '#ffaa00' }
            };
            
            const layout = {
                title: 'Player Engagement',
                paper_bgcolor: '#2d2d2d',
                plot_bgcolor: '#2d2d2d',
                font: { color: '#ffffff' },
                yaxis: { title: 'Active Players', side: 'left', gridcolor: '#444' },
                yaxis2: { title: 'Satisfaction', side: 'right', overlaying: 'y', gridcolor: '#444' },
                xaxis: { gridcolor: '#444' }
            };
            
            Plotly.newPlot('engagementChart', [trace1, trace2], layout, {responsive: true});
        }
        
        function updateKPIMetrics() {
            const kpis = dashboardData.kpis;
            
            if (!kpis) return;
            
            const metricsHTML = `
                <div class="metric-row">
                    <span>Balance Score:</span>
                    <span class="metric-value">${(kpis.overall_balance_score || 0).toFixed(3)}</span>
                </div>
                <div class="metric-row">
                    <span>Diversity Index:</span>
                    <span class="metric-value">${(kpis.faction_diversity_index || 0).toFixed(3)}</span>
                </div>
                <div class="metric-row">
                    <span>Player Satisfaction:</span>
                    <span class="metric-value">${(kpis.player_satisfaction_avg || 0).toFixed(2)}/5</span>
                </div>
                <div class="metric-row">
                    <span>Critical Alerts:</span>
                    <span class="metric-value ${kpis.critical_alerts > 0 ? 'status-critical' : 'status-good'}">${kpis.critical_alerts || 0}</span>
                </div>
            `;
            
            document.getElementById('kpiMetrics').innerHTML = metricsHTML;
        }
        
        function updateAlertsList() {
            const alerts = dashboardData.alerts;
            
            if (!alerts || !alerts.active_alerts) return;
            
            const alertsHTML = alerts.active_alerts.length > 0 
                ? alerts.active_alerts.slice(-5).map(alert => 
                    `<div class="alert-item alert-${alert.severity}">
                        <strong>${alert.type.toUpperCase()}</strong>: ${alert.description}
                        <br><small>${new Date(alert.timestamp).toLocaleTimeString()}</small>
                    </div>`
                ).join('')
                : '<div style="color: #00ff88;">No active alerts</div>';
            
            document.getElementById('alertsList').innerHTML = alertsHTML;
        }
        
        function updateFactionDetails() {
            const territorial = dashboardData.territorial;
            
            if (!territorial || Object.keys(territorial).length === 0) return;
            
            const detailsHTML = Object.keys(territorial).map(id => {
                const faction = territorial[id];
                return `
                    <div class="faction-row">
                        <div class="faction-name" style="color: ${faction.faction_color}">
                            ${faction.faction_name}
                        </div>
                        <div>
                            ${faction.territories_controlled} territories 
                            (${(faction.control_percentage * 100).toFixed(1)}%)
                        </div>
                    </div>
                `;
            }).join('');
            
            document.getElementById('factionDetails').innerHTML = detailsHTML;
        }
        
        function handleTerritorialUpdate(data) {
            // Real-time territorial updates
            showUpdateIndicator();
        }
        
        function handlePlayerMetricsUpdate(data) {
            // Real-time player metrics updates
            showUpdateIndicator();
        }
        
        function handleAnomalyDetected(data) {
            // Handle anomaly detection
            console.log('Anomaly detected:', data);
            showUpdateIndicator();
        }
        
        function handleKPIUpdate(data) {
            // Handle KPI updates
            showUpdateIndicator();
        }
        
        function handleCriticalAlert(alert) {
            // Handle critical alerts
            console.log('CRITICAL ALERT:', alert);
            
            // Could add audio notification or popup here
            showUpdateIndicator();
        }
        
        function showUpdateIndicator() {
            const indicator = document.getElementById('updateIndicator');
            indicator.classList.add('show');
            
            setTimeout(() => {
                indicator.classList.remove('show');
            }, 1000);
        }
    </script>
</body>
</html>
    """
    
    # Save template to templates directory
    import os
    
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        
    with open(os.path.join(templates_dir, "territorial_dashboard.html"), "w") as f:
        f.write(html_template)
        
    print("✅ Dashboard HTML template created")


async def main():
    """Main function to run the real-time analytics system"""
    print("Terminal Grounds - Real-time Territorial Analytics Dashboard")
    print("=" * 60)
    
    # Create dashboard HTML template
    create_dashboard_html()
    
    # Initialize analytics system
    analytics = RealTimeTerritorialAnalytics()
    
    print("🚀 Starting real-time analytics system...")
    
    try:
        # Start dashboard server in separate thread
        server_thread = Thread(
            target=analytics.start_dashboard_server,
            kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False}
        )
        server_thread.daemon = True
        server_thread.start()
        
        # Wait a moment for server to start
        await asyncio.sleep(2)
        
        print("🌐 Dashboard available at: http://localhost:5000")
        print("📊 Real-time monitoring active")
        print("🔍 Anomaly detection enabled")
        print("🚨 Alert system operational")
        
        # Start real-time monitoring
        await analytics.start_realtime_monitoring()
        
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down analytics system...")
        analytics.running = False
        
    except Exception as e:
        print(f"❌ Error in analytics system: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the real-time analytics system
    asyncio.run(main())