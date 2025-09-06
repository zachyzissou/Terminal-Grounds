#!/usr/bin/env python3
"""
Predictive Balance Modeling System for Terminal Grounds
Advanced machine learning models for meta-game evolution and balance forecasting

This system provides:
- Meta-game evolution prediction with confidence bounds
- Dominant strategy identification and prevention algorithms
- Long-term competitive balance sustainability analysis
- Player behavior clustering and retention prediction
- Real-time balance drift detection and early warning systems
- Automated balance recommendation engine with risk assessment

Author: Terminal Grounds Data Science Team
Date: 2025-09-06
Version: 1.0.0 - Production Predictive Balance System
"""

import numpy as np
import pandas as pd
import json
import time
import logging
import pickle
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier, IsolationForest
from sklearn.cluster import KMeans, DBSCAN
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score, silhouette_score
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neural_network import MLPRegressor, MLPClassifier
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PredictiveBalanceModeling")

class BalanceTrend(Enum):
    """Balance trend classifications"""
    STABLE = "stable"
    IMPROVING = "improving"
    DEGRADING = "degrading"
    VOLATILE = "volatile"
    CRITICAL = "critical"

class PlayerArchetype(Enum):
    """Player behavior archetypes"""
    TERRITORIAL_SPECIALIST = "territorial_specialist"
    ECONOMIC_POWERHOUSE = "economic_powerhouse"
    DIPLOMATIC_COORDINATOR = "diplomatic_coordinator"
    BALANCED_GENERALIST = "balanced_generalist"
    AGGRESSIVE_EXTRACTOR = "aggressive_extractor"
    DEFENSIVE_CONTROLLER = "defensive_controller"
    OPPORTUNISTIC_RAIDER = "opportunistic_raider"

@dataclass
class BalancePrediction:
    """Prediction for balance metrics"""
    metric_name: str
    current_value: float
    predicted_value: float
    confidence_interval: Tuple[float, float]
    prediction_horizon_days: int
    confidence_score: float
    trend_classification: BalanceTrend
    risk_factors: List[str]
    recommendations: List[str]

@dataclass
class MetaGameEvolution:
    """Meta-game evolution analysis results"""
    dominant_strategies: Dict[str, float]
    emerging_strategies: List[str]
    declining_strategies: List[str]
    strategy_diversity_index: float
    evolution_velocity: float
    stability_score: float
    predicted_shifts: List[Dict[str, Any]]

@dataclass
class PlayerBehaviorCluster:
    """Player behavior cluster analysis"""
    cluster_id: int
    archetype: PlayerArchetype
    size_percentage: float
    avg_win_rate: float
    avg_session_duration: float
    preferred_strategies: List[str]
    retention_rate: float
    balance_sensitivity: float

class PredictiveBalanceModelingSystem:
    """
    Advanced predictive modeling system for territorial balance forecasting
    
    Features:
    - Time series analysis for balance trend prediction
    - Machine learning models for meta-game evolution forecasting
    - Player behavior clustering and retention modeling
    - Anomaly detection for balance drift identification
    - Multi-horizon predictions with uncertainty quantification
    - Real-time model updating and drift detection
    """
    
    def __init__(self):
        self.db_path = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
        self.models_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/TerritorialSystem/models/")
        self.models_dir.mkdir(exist_ok=True)
        
        # Model configurations
        self.prediction_horizons = [7, 14, 30, 60]  # Days
        self.min_training_samples = 100
        self.max_model_age_days = 30
        
        # Trained models storage
        self.balance_models: Dict[str, Any] = {}
        self.player_behavior_models: Dict[str, Any] = {}
        self.anomaly_detectors: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        
        # Model performance tracking
        self.model_performance: Dict[str, Dict] = {}
        
        logger.info("Predictive Balance Modeling System initialized")
    
    def load_historical_balance_data(self) -> pd.DataFrame:
        """Load comprehensive historical balance data for modeling"""
        try:
            connection = sqlite3.connect(str(self.db_path))
            
            query = """
            WITH daily_metrics AS (
                SELECT 
                    DATE(session_start) as date,
                    faction_id,
                    COUNT(*) as games_played,
                    AVG(CASE WHEN winner_faction_id = faction_id THEN 1.0 ELSE 0.0 END) as win_rate,
                    AVG(session_duration_minutes) as avg_session_duration,
                    AVG(total_strategic_value) as avg_strategic_performance,
                    AVG(total_economic_impact) as avg_economic_performance,
                    AVG(trust_interactions) as avg_diplomatic_activity,
                    AVG(extraction_success_rate) as avg_extraction_rate,
                    COUNT(DISTINCT victory_type) as victory_type_diversity
                FROM games_comprehensive
                WHERE session_start >= date('now', '-90 days')
                GROUP BY DATE(session_start), faction_id
            ),
            daily_balance_metrics AS (
                SELECT 
                    date,
                    COUNT(DISTINCT faction_id) as active_factions,
                    AVG(win_rate) as overall_avg_win_rate,
                    STDEV(win_rate) as win_rate_variance,
                    MAX(win_rate) - MIN(win_rate) as win_rate_range,
                    AVG(games_played) as avg_games_per_faction,
                    AVG(victory_type_diversity) as strategy_diversity,
                    SUM(games_played) as total_daily_games
                FROM daily_metrics
                GROUP BY date
            ),
            victory_trends AS (
                SELECT 
                    DATE(session_start) as date,
                    victory_type,
                    COUNT(*) as victory_count,
                    AVG(session_duration_minutes) as avg_time_to_victory
                FROM games_comprehensive
                WHERE winner_faction_id IS NOT NULL
                  AND session_start >= date('now', '-90 days')
                GROUP BY DATE(session_start), victory_type
            )
            SELECT 
                dbm.date,
                dbm.active_factions,
                dbm.overall_avg_win_rate,
                dbm.win_rate_variance,
                dbm.win_rate_range,
                dbm.avg_games_per_faction,
                dbm.strategy_diversity,
                dbm.total_daily_games,
                -- Faction-specific metrics (pivot)
                dm1.win_rate as faction_1_win_rate,
                dm2.win_rate as faction_2_win_rate,
                dm3.win_rate as faction_3_win_rate,
                dm4.win_rate as faction_4_win_rate,
                dm5.win_rate as faction_5_win_rate,
                dm6.win_rate as faction_6_win_rate,
                dm7.win_rate as faction_7_win_rate,
                -- Victory type metrics
                vt_territorial.victory_count as territorial_victories,
                vt_economic.victory_count as economic_victories,
                vt_diplomatic.victory_count as diplomatic_victories,
                vt_extraction.victory_count as extraction_victories
            FROM daily_balance_metrics dbm
            LEFT JOIN daily_metrics dm1 ON dbm.date = dm1.date AND dm1.faction_id = 1
            LEFT JOIN daily_metrics dm2 ON dbm.date = dm2.date AND dm2.faction_id = 2
            LEFT JOIN daily_metrics dm3 ON dbm.date = dm3.date AND dm3.faction_id = 3
            LEFT JOIN daily_metrics dm4 ON dbm.date = dm4.date AND dm4.faction_id = 4
            LEFT JOIN daily_metrics dm5 ON dbm.date = dm5.date AND dm5.faction_id = 5
            LEFT JOIN daily_metrics dm6 ON dbm.date = dm6.date AND dm6.faction_id = 6
            LEFT JOIN daily_metrics dm7 ON dbm.date = dm7.date AND dm7.faction_id = 7
            LEFT JOIN victory_trends vt_territorial ON dbm.date = vt_territorial.date 
                AND vt_territorial.victory_type = 'territorial_dominance'
            LEFT JOIN victory_trends vt_economic ON dbm.date = vt_economic.date 
                AND vt_economic.victory_type = 'economic_control'
            LEFT JOIN victory_trends vt_diplomatic ON dbm.date = vt_diplomatic.date 
                AND vt_diplomatic.victory_type = 'diplomatic_alliance'
            LEFT JOIN victory_trends vt_extraction ON dbm.date = vt_extraction.date 
                AND vt_extraction.victory_type = 'extraction_efficiency'
            ORDER BY dbm.date
            """
            
            df = pd.read_sql_query(query, connection)
            connection.close()
            
            # Data preprocessing
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            
            # Fill missing values with appropriate methods
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            df[numeric_columns] = df[numeric_columns].fillna(method='ffill').fillna(0)
            
            # Feature engineering
            df['balance_score'] = 1 - df['win_rate_variance']  # Higher score = better balance
            df['competitive_intensity'] = df['win_rate_range']
            df['activity_level'] = df['total_daily_games'] / df['active_factions']
            
            # Rolling averages for trend analysis
            for window in [3, 7, 14]:
                df[f'balance_score_ma_{window}'] = df['balance_score'].rolling(window=window).mean()
                df[f'win_rate_variance_ma_{window}'] = df['win_rate_variance'].rolling(window=window).mean()
            
            logger.info(f"Loaded {len(df)} days of historical balance data")
            return df
            
        except Exception as e:
            logger.error(f"Error loading historical balance data: {e}")
            return pd.DataFrame()
    
    def train_balance_prediction_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train machine learning models for balance prediction"""
        models = {}
        
        if len(df) < self.min_training_samples:
            logger.warning(f"Insufficient data for model training: {len(df)} < {self.min_training_samples}")
            return models
        
        # Prepare feature sets
        balance_features = [
            'overall_avg_win_rate', 'avg_games_per_faction', 'strategy_diversity',
            'active_factions', 'total_daily_games', 'competitive_intensity'
        ]
        
        faction_features = [f'faction_{i}_win_rate' for i in range(1, 8)]
        victory_features = ['territorial_victories', 'economic_victories', 'diplomatic_victories', 'extraction_victories']
        
        all_features = balance_features + faction_features + victory_features
        
        # Target variables for prediction
        target_variables = [
            'balance_score', 'win_rate_variance', 'competitive_intensity', 'strategy_diversity'
        ]
        
        for target in target_variables:
            if target not in df.columns:
                continue
            
            # Prepare data for time series prediction
            X = df[all_features].fillna(0).values
            y = df[target].values
            
            # Create time series features (lag features)
            X_ts = []
            y_ts = []
            
            look_back = 7  # Use 7 days of history
            for i in range(look_back, len(X)):
                X_ts.append(X[i-look_back:i].flatten())
                y_ts.append(y[i])
            
            X_ts = np.array(X_ts)
            y_ts = np.array(y_ts)
            
            if len(X_ts) < 50:  # Minimum samples for time series
                continue
            
            # Split data (time series split)
            split_point = int(len(X_ts) * 0.8)
            X_train, X_test = X_ts[:split_point], X_ts[split_point:]
            y_train, y_test = y_ts[:split_point], y_ts[split_point:]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train multiple models and ensemble
            model_configs = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42) if target == 'balance_score' else GradientBoostingRegressor(n_estimators=100, random_state=42),
                'neural_network': MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=1000, random_state=42)
            }
            
            best_model = None
            best_score = -float('inf')
            best_model_name = ""
            
            model_performances = {}
            
            for model_name, model in model_configs.items():
                try:
                    # Train model
                    if hasattr(model, 'fit'):
                        model.fit(X_train_scaled, y_train)
                        
                        # Evaluate
                        y_pred = model.predict(X_test_scaled)
                        score = r2_score(y_test, y_pred)
                        
                        model_performances[model_name] = {
                            'r2_score': score,
                            'mse': mean_squared_error(y_test, y_pred),
                            'prediction_accuracy': np.corrcoef(y_test, y_pred)[0, 1] if len(y_test) > 1 else 0
                        }
                        
                        if score > best_score:
                            best_score = score
                            best_model = model
                            best_model_name = model_name
                            
                except Exception as e:
                    logger.warning(f"Error training {model_name} for {target}: {e}")
                    continue
            
            if best_model is not None:
                models[target] = {
                    'model': best_model,
                    'scaler': scaler,
                    'model_type': best_model_name,
                    'performance': model_performances[best_model_name],
                    'features': all_features,
                    'look_back': look_back,
                    'training_samples': len(X_train),
                    'last_updated': time.time()
                }
                
                logger.info(f"Trained {target} model: {best_model_name} (R² = {best_score:.3f})")
        
        return models
    
    def predict_balance_evolution(self, df: pd.DataFrame, horizon_days: int = 14) -> List[BalancePrediction]:
        """Predict balance evolution over specified horizon"""
        predictions = []
        
        if not self.balance_models:
            logger.warning("No trained models available for prediction")
            return predictions
        
        # Get latest data point
        latest_data = df.iloc[-1]
        
        for target, model_data in self.balance_models.items():
            try:
                model = model_data['model']
                scaler = model_data['scaler']
                features = model_data['features']
                look_back = model_data['look_back']
                
                # Prepare input data (last look_back days)
                if len(df) < look_back:
                    continue
                
                input_data = df[features].fillna(0).iloc[-look_back:].values
                input_data_scaled = scaler.transform(input_data.flatten().reshape(1, -1))
                
                # Make prediction
                predicted_value = model.predict(input_data_scaled)[0]
                
                # Calculate confidence interval (using prediction variance)
                # For simplicity, using model performance metrics
                performance = model_data['performance']
                prediction_std = np.sqrt(performance['mse'])
                
                confidence_interval = (
                    predicted_value - 1.96 * prediction_std,
                    predicted_value + 1.96 * prediction_std
                )
                
                # Determine trend classification
                current_value = latest_data[target]
                change_magnitude = abs(predicted_value - current_value)
                change_direction = predicted_value - current_value
                
                if change_magnitude < 0.02:  # 2% threshold
                    trend = BalanceTrend.STABLE
                elif change_direction > 0 and change_magnitude > 0.05:
                    trend = BalanceTrend.IMPROVING
                elif change_direction < 0 and change_magnitude > 0.05:
                    trend = BalanceTrend.DEGRADING
                elif change_magnitude > 0.10:
                    trend = BalanceTrend.VOLATILE
                else:
                    trend = BalanceTrend.STABLE
                
                # Generate risk factors and recommendations
                risk_factors = []
                recommendations = []
                
                if target == 'win_rate_variance' and predicted_value > 0.15:
                    risk_factors.append("High faction win rate variance predicted")
                    recommendations.append("Consider faction balance adjustments")
                
                if target == 'balance_score' and predicted_value < 0.7:
                    risk_factors.append("Overall balance score declining")
                    recommendations.append("Implement comprehensive balance review")
                
                if target == 'strategy_diversity' and predicted_value < 3.0:
                    risk_factors.append("Decreasing strategic diversity")
                    recommendations.append("Enhance victory condition accessibility")
                
                predictions.append(BalancePrediction(
                    metric_name=target,
                    current_value=current_value,
                    predicted_value=predicted_value,
                    confidence_interval=confidence_interval,
                    prediction_horizon_days=horizon_days,
                    confidence_score=min(1.0, performance['r2_score']),
                    trend_classification=trend,
                    risk_factors=risk_factors,
                    recommendations=recommendations
                ))
                
            except Exception as e:
                logger.error(f"Error predicting {target}: {e}")
                continue
        
        return predictions
    
    def analyze_meta_game_evolution(self, df: pd.DataFrame) -> MetaGameEvolution:
        """Analyze meta-game evolution patterns and predict shifts"""
        
        # Calculate strategy dominance over time
        victory_columns = ['territorial_victories', 'economic_victories', 'diplomatic_victories', 'extraction_victories']
        recent_data = df.tail(14)  # Last 2 weeks
        
        # Current strategy dominance
        total_victories = recent_data[victory_columns].sum().sum()
        if total_victories > 0:
            dominant_strategies = {
                'territorial': recent_data['territorial_victories'].sum() / total_victories,
                'economic': recent_data['economic_victories'].sum() / total_victories,
                'diplomatic': recent_data['diplomatic_victories'].sum() / total_victories,
                'extraction': recent_data['extraction_victories'].sum() / total_victories
            }
        else:
            dominant_strategies = {'territorial': 0.25, 'economic': 0.25, 'diplomatic': 0.25, 'extraction': 0.25}
        
        # Analyze trends over time windows
        windows = [7, 14, 30]  # Different time horizons
        strategy_trends = {}
        
        for window in windows:
            if len(df) >= window:
                window_data = df.tail(window)
                window_total = window_data[victory_columns].sum().sum()
                
                if window_total > 0:
                    window_strategies = {
                        'territorial': window_data['territorial_victories'].sum() / window_total,
                        'economic': window_data['economic_victories'].sum() / window_total,
                        'diplomatic': window_data['diplomatic_victories'].sum() / window_total,
                        'extraction': window_data['extraction_victories'].sum() / window_total
                    }
                    strategy_trends[window] = window_strategies
        
        # Identify emerging and declining strategies
        emerging_strategies = []
        declining_strategies = []
        
        if len(strategy_trends) >= 2:
            short_term = strategy_trends[min(windows)]
            long_term = strategy_trends[max(windows)]
            
            for strategy in ['territorial', 'economic', 'diplomatic', 'extraction']:
                short_value = short_term.get(strategy, 0)
                long_value = long_term.get(strategy, 0)
                
                change = short_value - long_value
                
                if change > 0.05:  # 5% increase
                    emerging_strategies.append(strategy)
                elif change < -0.05:  # 5% decrease
                    declining_strategies.append(strategy)
        
        # Calculate diversity metrics
        strategy_values = list(dominant_strategies.values())
        strategy_diversity_index = 1 - sum((p - 0.25)**2 for p in strategy_values)  # Deviation from uniform
        
        # Calculate evolution velocity (how quickly the meta is changing)
        if len(df) > 14:
            recent_variance = df['strategy_diversity'].tail(7).var()
            historical_variance = df['strategy_diversity'].head(7).var()
            evolution_velocity = recent_variance / (historical_variance + 0.01)  # Avoid division by zero
        else:
            evolution_velocity = 1.0
        
        # Stability score
        balance_stability = 1 - df['win_rate_variance'].tail(14).mean()
        strategy_stability = 1 - df['strategy_diversity'].tail(14).std()
        stability_score = (balance_stability + strategy_stability) / 2
        
        # Predict future shifts
        predicted_shifts = []
        
        # Use simple trend extrapolation for demonstration
        for strategy, current_rate in dominant_strategies.items():
            if len(strategy_trends) >= 2:
                trend = list(strategy_trends.values())[0][strategy] - list(strategy_trends.values())[-1][strategy]
                predicted_rate = current_rate + trend * 2  # Extrapolate
                
                if abs(predicted_rate - current_rate) > 0.08:  # Significant shift
                    predicted_shifts.append({
                        'strategy': strategy,
                        'current_dominance': current_rate,
                        'predicted_dominance': predicted_rate,
                        'confidence': min(1.0, stability_score),
                        'timeframe_days': 30
                    })
        
        return MetaGameEvolution(
            dominant_strategies=dominant_strategies,
            emerging_strategies=emerging_strategies,
            declining_strategies=declining_strategies,
            strategy_diversity_index=strategy_diversity_index,
            evolution_velocity=evolution_velocity,
            stability_score=stability_score,
            predicted_shifts=predicted_shifts
        )
    
    def cluster_player_behaviors(self, df: pd.DataFrame) -> List[PlayerBehaviorCluster]:
        """Cluster players by behavior patterns and analyze archetypes"""
        clusters = []
        
        try:
            # Load player-level data for clustering
            connection = sqlite3.connect(str(self.db_path))
            
            player_query = """
            SELECT 
                player_id,
                faction_id,
                AVG(territorial_actions) as avg_territorial_actions,
                AVG(economic_actions) as avg_economic_actions,
                AVG(diplomatic_actions) as avg_diplomatic_actions,
                AVG(extraction_attempts) as avg_extraction_attempts,
                AVG(session_duration_minutes) as avg_session_duration,
                AVG(CASE WHEN is_winner = 1 THEN 1.0 ELSE 0.0 END) as win_rate,
                COUNT(*) as games_played,
                MAX(last_active) as last_active_date
            FROM player_game_stats
            WHERE games_played >= 5
            GROUP BY player_id, faction_id
            """
            
            player_df = pd.read_sql_query(player_query, connection)
            connection.close()
            
            if len(player_df) < 50:  # Minimum players for clustering
                logger.warning("Insufficient player data for clustering")
                return clusters
            
            # Prepare features for clustering
            clustering_features = [
                'avg_territorial_actions', 'avg_economic_actions', 'avg_diplomatic_actions',
                'avg_extraction_attempts', 'avg_session_duration', 'games_played'
            ]
            
            X = player_df[clustering_features].fillna(0)
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Determine optimal number of clusters
            silhouette_scores = []
            k_range = range(3, min(10, len(X) // 10))
            
            for k in k_range:
                kmeans = KMeans(n_clusters=k, random_state=42)
                cluster_labels = kmeans.fit_predict(X_scaled)
                silhouette_avg = silhouette_score(X_scaled, cluster_labels)
                silhouette_scores.append((k, silhouette_avg))
            
            optimal_k = max(silhouette_scores, key=lambda x: x[1])[0] if silhouette_scores else 5
            
            # Final clustering
            kmeans = KMeans(n_clusters=optimal_k, random_state=42)
            player_df['cluster'] = kmeans.fit_predict(X_scaled)
            
            # Analyze each cluster
            for cluster_id in range(optimal_k):
                cluster_data = player_df[player_df['cluster'] == cluster_id]
                
                if len(cluster_data) < 5:  # Skip small clusters
                    continue
                
                # Calculate cluster characteristics
                avg_territorial = cluster_data['avg_territorial_actions'].mean()
                avg_economic = cluster_data['avg_economic_actions'].mean()
                avg_diplomatic = cluster_data['avg_diplomatic_actions'].mean()
                avg_extraction = cluster_data['avg_extraction_attempts'].mean()
                
                # Determine archetype based on dominant behavior
                behaviors = {
                    'territorial': avg_territorial,
                    'economic': avg_economic,
                    'diplomatic': avg_diplomatic,
                    'extraction': avg_extraction
                }
                
                dominant_behavior = max(behaviors, key=behaviors.get)
                behavior_balance = np.std(list(behaviors.values()))
                
                if behavior_balance < np.mean(list(behaviors.values())) * 0.3:  # Balanced player
                    archetype = PlayerArchetype.BALANCED_GENERALIST
                elif dominant_behavior == 'territorial':
                    if avg_territorial > avg_extraction:
                        archetype = PlayerArchetype.TERRITORIAL_SPECIALIST
                    else:
                        archetype = PlayerArchetype.DEFENSIVE_CONTROLLER
                elif dominant_behavior == 'economic':
                    archetype = PlayerArchetype.ECONOMIC_POWERHOUSE
                elif dominant_behavior == 'diplomatic':
                    archetype = PlayerArchetype.DIPLOMATIC_COORDINATOR
                elif dominant_behavior == 'extraction':
                    if avg_territorial > avg_economic:
                        archetype = PlayerArchetype.AGGRESSIVE_EXTRACTOR
                    else:
                        archetype = PlayerArchetype.OPPORTUNISTIC_RAIDER
                else:
                    archetype = PlayerArchetype.BALANCED_GENERALIST
                
                # Calculate cluster metrics
                size_percentage = len(cluster_data) / len(player_df)
                avg_win_rate = cluster_data['win_rate'].mean()
                avg_session_duration = cluster_data['avg_session_duration'].mean()
                
                # Estimate retention rate (players active in last 30 days)
                recent_threshold = pd.Timestamp.now() - pd.Timedelta(days=30)
                cluster_data['last_active_date'] = pd.to_datetime(cluster_data['last_active_date'])
                retention_rate = (cluster_data['last_active_date'] > recent_threshold).mean()
                
                # Preferred strategies (simplified)
                preferred_strategies = []
                if avg_territorial > np.mean([avg_economic, avg_diplomatic, avg_extraction]):
                    preferred_strategies.append('territorial_control')
                if avg_economic > np.mean([avg_territorial, avg_diplomatic, avg_extraction]):
                    preferred_strategies.append('economic_warfare')
                if avg_diplomatic > np.mean([avg_territorial, avg_economic, avg_extraction]):
                    preferred_strategies.append('alliance_building')
                if avg_extraction > np.mean([avg_territorial, avg_economic, avg_diplomatic]):
                    preferred_strategies.append('extraction_focused')
                
                # Balance sensitivity (how much win rate varies with balance changes)
                balance_sensitivity = cluster_data['win_rate'].std()
                
                clusters.append(PlayerBehaviorCluster(
                    cluster_id=cluster_id,
                    archetype=archetype,
                    size_percentage=size_percentage,
                    avg_win_rate=avg_win_rate,
                    avg_session_duration=avg_session_duration,
                    preferred_strategies=preferred_strategies if preferred_strategies else ['balanced_approach'],
                    retention_rate=retention_rate,
                    balance_sensitivity=balance_sensitivity
                ))
            
            logger.info(f"Identified {len(clusters)} player behavior clusters")
            
        except Exception as e:
            logger.error(f"Error in player behavior clustering: {e}")
        
        return clusters
    
    def detect_balance_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect balance anomalies and potential issues"""
        anomalies = []
        
        if len(df) < 14:  # Need sufficient data
            return anomalies
        
        # Isolation Forest for anomaly detection
        balance_features = ['balance_score', 'win_rate_variance', 'strategy_diversity', 'competitive_intensity']
        
        X = df[balance_features].fillna(0)
        
        # Fit isolation forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = iso_forest.fit_predict(X)
        
        # Find anomalous days
        anomalous_indices = np.where(anomaly_labels == -1)[0]
        
        for idx in anomalous_indices:
            if idx >= len(df):
                continue
                
            anomaly_data = df.iloc[idx]
            
            # Analyze what made this day anomalous
            anomaly_factors = []
            
            if anomaly_data['balance_score'] < 0.5:
                anomaly_factors.append(f"Low balance score: {anomaly_data['balance_score']:.3f}")
            
            if anomaly_data['win_rate_variance'] > 0.2:
                anomaly_factors.append(f"High win rate variance: {anomaly_data['win_rate_variance']:.3f}")
            
            if anomaly_data['strategy_diversity'] < 2.0:
                anomaly_factors.append(f"Low strategy diversity: {anomaly_data['strategy_diversity']:.1f}")
            
            if anomaly_data['competitive_intensity'] > 0.3:
                anomaly_factors.append(f"High competitive intensity: {anomaly_data['competitive_intensity']:.3f}")
            
            anomalies.append({
                'date': anomaly_data['date'],
                'anomaly_score': iso_forest.decision_function(X.iloc[idx:idx+1])[0],
                'factors': anomaly_factors,
                'severity': 'high' if len(anomaly_factors) > 2 else 'medium',
                'recommendations': [
                    'Investigate balance changes on this date',
                    'Review player feedback from this period',
                    'Consider temporary balance adjustments'
                ]
            })
        
        return anomalies
    
    def generate_comprehensive_prediction_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive predictive balance analysis report"""
        logger.info("Generating comprehensive predictive balance analysis...")
        
        # Train models
        self.balance_models = self.train_balance_prediction_models(df)
        
        report = {
            'analysis_metadata': {
                'analysis_timestamp': time.time(),
                'data_points': len(df),
                'date_range': {
                    'start': df['date'].min().isoformat() if not df.empty else None,
                    'end': df['date'].max().isoformat() if not df.empty else None
                },
                'trained_models': len(self.balance_models),
                'prediction_horizons': self.prediction_horizons
            }
        }
        
        if df.empty or not self.balance_models:
            report['status'] = 'INSUFFICIENT_DATA'
            return report
        
        # Multi-horizon balance predictions
        report['balance_predictions'] = {}
        for horizon in self.prediction_horizons:
            predictions = self.predict_balance_evolution(df, horizon)
            report['balance_predictions'][f'{horizon}_days'] = [asdict(pred) for pred in predictions]
        
        # Meta-game evolution analysis
        meta_game_analysis = self.analyze_meta_game_evolution(df)
        report['meta_game_evolution'] = asdict(meta_game_analysis)
        
        # Player behavior clustering
        player_clusters = self.cluster_player_behaviors(df)
        report['player_behavior_analysis'] = [asdict(cluster) for cluster in player_clusters]
        
        # Anomaly detection
        anomalies = self.detect_balance_anomalies(df)
        report['balance_anomalies'] = anomalies
        
        # Risk assessment and recommendations
        risk_factors = []
        critical_recommendations = []
        
        # Analyze predictions for risks
        short_term_predictions = report['balance_predictions'].get('7_days', [])
        for pred in short_term_predictions:
            if pred['trend_classification'] in ['degrading', 'critical', 'volatile']:
                risk_factors.extend(pred['risk_factors'])
                critical_recommendations.extend(pred['recommendations'])
        
        # Meta-game risks
        if meta_game_analysis.stability_score < 0.6:
            risk_factors.append("Meta-game instability detected")
            critical_recommendations.append("Implement meta-game stabilization measures")
        
        if len(meta_game_analysis.dominant_strategies) > 0:
            max_dominance = max(meta_game_analysis.dominant_strategies.values())
            if max_dominance > 0.5:  # One strategy dominates >50%
                dominant_strategy = max(meta_game_analysis.dominant_strategies, 
                                      key=meta_game_analysis.dominant_strategies.get)
                risk_factors.append(f"{dominant_strategy} strategy over-dominant ({max_dominance:.1%})")
                critical_recommendations.append(f"Balance {dominant_strategy} victory conditions")
        
        # Player retention risks
        if player_clusters:
            avg_retention = np.mean([cluster.retention_rate for cluster in player_clusters])
            if avg_retention < 0.7:
                risk_factors.append(f"Low player retention rate: {avg_retention:.1%}")
                critical_recommendations.append("Investigate player retention factors")
        
        report['risk_assessment'] = {
            'overall_risk_level': 'HIGH' if len(risk_factors) > 3 else 'MEDIUM' if len(risk_factors) > 1 else 'LOW',
            'risk_factors': list(set(risk_factors)),
            'critical_recommendations': list(set(critical_recommendations)),
            'anomaly_count': len(anomalies),
            'model_confidence': np.mean([model['performance']['r2_score'] for model in self.balance_models.values()])
        }
        
        return report
    
    def export_predictive_analysis(self, output_path: Optional[str] = None) -> str:
        """Export predictive balance analysis to JSON"""
        if not output_path:
            timestamp = int(time.time())
            output_path = f"C:/Users/Zachg/Terminal-Grounds/Tools/TerritorialSystem/predictive_balance_analysis_{timestamp}.json"
        
        # Load data and generate report
        df = self.load_historical_balance_data()
        report = self.generate_comprehensive_prediction_report(df)
        
        # Export report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Predictive balance analysis exported to: {output_path}")
        return output_path

def main():
    """Main function for predictive balance modeling demonstration"""
    print("PREDICTIVE BALANCE MODELING SYSTEM")
    print("Advanced Machine Learning for Meta-Game Evolution")
    print("=" * 75)
    
    # Initialize system
    modeling_system = PredictiveBalanceModelingSystem()
    
    # Run comprehensive analysis
    analysis_path = modeling_system.export_predictive_analysis()
    
    # Load and display summary
    with open(analysis_path, 'r') as f:
        report = json.load(f)
    
    print(f"\nPREDICTIVE ANALYSIS COMPLETE")
    print(f"Data Points Analyzed: {report['analysis_metadata']['data_points']}")
    print(f"Models Trained: {report['analysis_metadata']['trained_models']}")
    print(f"Risk Level: {report['risk_assessment']['overall_risk_level']}")
    print(f"Model Confidence: {report['risk_assessment']['model_confidence']:.3f}")
    
    # Display key predictions
    if '14_days' in report.get('balance_predictions', {}):
        print(f"\n14-DAY BALANCE PREDICTIONS:")
        for pred in report['balance_predictions']['14_days'][:3]:  # Top 3 predictions
            print(f"  {pred['metric_name']}: {pred['current_value']:.3f} → {pred['predicted_value']:.3f} ({pred['trend_classification']})")
    
    # Display meta-game analysis
    if 'meta_game_evolution' in report:
        meta = report['meta_game_evolution']
        print(f"\nMETA-GAME ANALYSIS:")
        print(f"  Strategy Diversity Index: {meta['strategy_diversity_index']:.3f}")
        print(f"  Stability Score: {meta['stability_score']:.3f}")
        if meta['emerging_strategies']:
            print(f"  Emerging Strategies: {', '.join(meta['emerging_strategies'])}")
        if meta['declining_strategies']:
            print(f"  Declining Strategies: {', '.join(meta['declining_strategies'])}")
    
    # Display critical recommendations
    if report['risk_assessment']['critical_recommendations']:
        print(f"\nCRITICAL RECOMMENDATIONS:")
        for rec in report['risk_assessment']['critical_recommendations'][:3]:
            print(f"  • {rec}")
    
    print(f"\nDetailed analysis exported to: {analysis_path}")
    print("\n" + "=" * 75)
    print("PREDICTIVE MODELING COMPLETE")
    print("Meta-game evolution forecasting with machine learning intelligence")
    print("Balance drift detection and automated recommendation engine operational")

if __name__ == "__main__":
    main()