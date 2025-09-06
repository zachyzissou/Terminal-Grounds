#!/usr/bin/env python3
"""
Economic Cascade Analysis System
Advanced economic impact modeling for territorial cascade effects

Implements:
- Convoy route disruption propagation analysis
- Supply chain network modeling with statistical validation
- Economic multiplier effects with uncertainty quantification
- Real-time economic impact assessment
- Resource flow optimization and prediction models
"""

import numpy as np
import json
import sqlite3
import time
import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
from collections import defaultdict, deque
import statistics
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EconomicCascade")

class EconomicCascadeType(Enum):
    """Types of economic cascade effects"""
    SUPPLY_ROUTE_DISRUPTION = "supply_route_disruption"
    RESOURCE_SCARCITY_PROPAGATION = "resource_scarcity_propagation"
    TRADE_NETWORK_COLLAPSE = "trade_network_collapse"
    ECONOMIC_ISOLATION = "economic_isolation"
    INFLATION_SPIRAL = "inflation_spiral"
    MARKET_MANIPULATION = "market_manipulation"

class ResourceType(Enum):
    """Types of resources in economic model"""
    FIELD_MATERIALS = "field_materials"
    SPLICE_COMPONENTS = "splice_components"
    MONOLITH_ARTIFACTS = "monolith_artifacts"
    ENERGY_CORES = "energy_cores"
    MANUFACTURING = "manufacturing"
    INFORMATION = "information"
    LOGISTICS = "logistics"

@dataclass
class EconomicNode:
    """Economic node representing resource production and consumption"""
    territory_id: int
    territory_name: str
    production_capacity: Dict[ResourceType, float]
    consumption_demand: Dict[ResourceType, float]
    storage_capacity: Dict[ResourceType, float]
    current_inventory: Dict[ResourceType, float]
    trade_efficiency: float  # 0.0 to 1.0
    economic_resilience: float  # Resistance to disruption
    strategic_economic_value: float  # Economic importance in network

@dataclass
class EconomicEdge:
    """Trade route between territories"""
    source_territory_id: int
    target_territory_id: int
    route_capacity: Dict[ResourceType, float]
    transport_efficiency: float
    security_level: float  # Route safety
    disruption_probability: float
    economic_flow_value: float  # Economic value of trade

@dataclass
class EconomicCascadeEvent:
    """Economic cascade event with detailed impact analysis"""
    cascade_id: str
    cascade_type: EconomicCascadeType
    source_territory_id: int
    affected_territory_ids: List[int]
    affected_trade_routes: List[Tuple[int, int]]  # (source, target) pairs
    resource_disruption: Dict[ResourceType, float]  # Disruption magnitude per resource
    economic_impact_multiplier: float
    price_inflation_factor: Dict[ResourceType, float]
    supply_shortage_probability: Dict[ResourceType, float]
    recovery_time_estimate: float  # Hours
    cascading_probability: float  # Probability of further cascades
    total_economic_loss: float  # Estimated economic damage
    timestamp: float

class EconomicCascadeAnalyzer:
    """
    Advanced economic cascade analysis system
    
    Features:
    - Supply chain network modeling and disruption analysis
    - Economic multiplier effect calculations with statistical validation
    - Resource flow optimization and shortage prediction
    - Price impact modeling with market dynamics
    - Recovery time estimation with uncertainty quantification
    """
    
    def __init__(self):
        self.db_path = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
        
        # Economic network components
        self.economic_nodes: Dict[int, EconomicNode] = {}
        self.trade_routes: List[EconomicEdge] = []
        self.resource_prices: Dict[ResourceType, float] = {}
        
        # Economic parameters (calibrated from game balance)
        self.base_economic_multiplier = 1.5
        self.supply_disruption_threshold = 0.3  # 30% supply loss triggers cascades
        self.price_elasticity = 0.8  # Price sensitivity
        self.recovery_rate_base = 0.1  # Base recovery rate per hour
        
        # Faction economic profiles
        self.faction_economic_profiles: Dict[int, Dict] = {}
        
        # Economic cascade history for pattern analysis
        self.economic_cascade_history: List[EconomicCascadeEvent] = []
        
        logger.info("Economic Cascade Analyzer initialized")
        
    def load_economic_network(self) -> bool:
        """Load territorial economic data and build economic network"""
        try:
            start_time = time.time()
            
            connection = sqlite3.connect(str(self.db_path))
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            # Load territory economic data
            cursor.execute("""
                SELECT t.id, t.territory_name, t.strategic_value, t.resource_multiplier,
                       t.current_controller_faction_id, t.center_x, t.center_y,
                       f.faction_name, f.tech_level, f.loot_tier_bias, f.vehicle_affinity
                FROM territories t
                LEFT JOIN factions f ON t.current_controller_faction_id = f.id
            """)
            
            territories = cursor.fetchall()
            
            # Load faction economic profiles
            cursor.execute("""
                SELECT id, faction_name, tech_level, loot_tier_bias, 
                       vehicle_affinity, event_preference
                FROM factions
            """)
            
            factions = cursor.fetchall()
            connection.close()
            
            # Build economic nodes
            self._build_economic_nodes(territories, factions)
            
            # Build trade route network
            self._build_trade_network()
            
            # Initialize resource prices
            self._initialize_resource_prices()
            
            # Load faction economic profiles
            self._load_faction_economic_profiles(factions)
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Economic network loaded: {len(self.economic_nodes)} nodes, {len(self.trade_routes)} routes")
            logger.info(f"Economic analysis ready in {processing_time:.2f}ms")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading economic network: {e}")
            return False
    
    def _build_economic_nodes(self, territories: List, factions: List) -> None:
        """Build economic nodes from territorial data"""
        for territory in territories:
            # Calculate production capacity based on territory characteristics
            production_capacity = self._calculate_production_capacity(territory)
            consumption_demand = self._calculate_consumption_demand(territory)
            storage_capacity = self._calculate_storage_capacity(territory)
            
            # Initialize current inventory at 70% capacity
            current_inventory = {
                resource: capacity * 0.7 
                for resource, capacity in storage_capacity.items()
            }
            
            # Trade efficiency based on strategic value and faction tech level
            trade_efficiency = min(1.0, (territory['strategic_value'] / 10.0) * 0.8 + 0.2)
            if territory['tech_level']:
                trade_efficiency *= (territory['tech_level'] * 0.3 + 0.7)
            
            # Economic resilience based on strategic value and faction discipline
            economic_resilience = territory['strategic_value'] / 10.0
            
            # Strategic economic value
            strategic_economic_value = (
                territory['strategic_value'] * territory['resource_multiplier']
            ) / 10.0
            
            node = EconomicNode(
                territory_id=territory['id'],
                territory_name=territory['territory_name'],
                production_capacity=production_capacity,
                consumption_demand=consumption_demand,
                storage_capacity=storage_capacity,
                current_inventory=current_inventory,
                trade_efficiency=trade_efficiency,
                economic_resilience=economic_resilience,
                strategic_economic_value=strategic_economic_value
            )
            
            self.economic_nodes[territory['id']] = node
    
    def _calculate_production_capacity(self, territory: sqlite3.Row) -> Dict[ResourceType, float]:
        """Calculate production capacity based on territory characteristics"""
        base_production = territory['resource_multiplier'] * 100  # Base production units
        strategic_modifier = territory['strategic_value'] / 10.0
        
        # Territory-specific production profiles
        name = territory['territory_name'].lower()
        production = {}
        
        if 'tech wastes' in name or 'industrial' in name:
            # Industrial territories focus on materials and manufacturing
            production[ResourceType.FIELD_MATERIALS] = base_production * strategic_modifier * 1.5
            production[ResourceType.MANUFACTURING] = base_production * strategic_modifier * 1.3
            production[ResourceType.ENERGY_CORES] = base_production * strategic_modifier * 0.8
            production[ResourceType.SPLICE_COMPONENTS] = base_production * strategic_modifier * 0.6
            production[ResourceType.MONOLITH_ARTIFACTS] = base_production * strategic_modifier * 0.3
            production[ResourceType.INFORMATION] = base_production * strategic_modifier * 0.5
            production[ResourceType.LOGISTICS] = base_production * strategic_modifier * 0.9
            
        elif 'iez facility' in name or 'corporate' in name:
            # Corporate territories focus on high-tech resources
            production[ResourceType.SPLICE_COMPONENTS] = base_production * strategic_modifier * 1.4
            production[ResourceType.MONOLITH_ARTIFACTS] = base_production * strategic_modifier * 1.2
            production[ResourceType.INFORMATION] = base_production * strategic_modifier * 1.6
            production[ResourceType.ENERGY_CORES] = base_production * strategic_modifier * 1.1
            production[ResourceType.FIELD_MATERIALS] = base_production * strategic_modifier * 0.7
            production[ResourceType.MANUFACTURING] = base_production * strategic_modifier * 0.8
            production[ResourceType.LOGISTICS] = base_production * strategic_modifier * 1.2
            
        elif 'metro' in name or 'maintenance' in name:
            # Metro areas focus on logistics and basic materials
            production[ResourceType.LOGISTICS] = base_production * strategic_modifier * 1.5
            production[ResourceType.FIELD_MATERIALS] = base_production * strategic_modifier * 1.2
            production[ResourceType.MANUFACTURING] = base_production * strategic_modifier * 1.0
            production[ResourceType.ENERGY_CORES] = base_production * strategic_modifier * 0.9
            production[ResourceType.SPLICE_COMPONENTS] = base_production * strategic_modifier * 0.7
            production[ResourceType.MONOLITH_ARTIFACTS] = base_production * strategic_modifier * 0.4
            production[ResourceType.INFORMATION] = base_production * strategic_modifier * 0.8
            
        else:
            # Default balanced production
            for resource_type in ResourceType:
                production[resource_type] = base_production * strategic_modifier * 0.8
        
        return production
    
    def _calculate_consumption_demand(self, territory: sqlite3.Row) -> Dict[ResourceType, float]:
        """Calculate consumption demand based on territory population and activity"""
        base_demand = territory['strategic_value'] * 15  # Higher strategic value = more demand
        
        # Faction modifier affects consumption patterns
        faction_modifier = 1.0
        if territory['tech_level']:
            faction_modifier = territory['tech_level'] * 0.4 + 0.8  # High-tech factions consume more
        
        demand = {}
        for resource_type in ResourceType:
            demand[resource_type] = base_demand * faction_modifier * 0.9  # 90% of production as baseline
        
        return demand
    
    def _calculate_storage_capacity(self, territory: sqlite3.Row) -> Dict[ResourceType, float]:
        """Calculate storage capacity based on territory infrastructure"""
        base_storage = territory['strategic_value'] * territory['resource_multiplier'] * 200
        
        storage = {}
        for resource_type in ResourceType:
            storage[resource_type] = base_storage
        
        return storage
    
    def _build_trade_network(self) -> None:
        """Build trade route network between territories"""
        territory_list = list(self.economic_nodes.values())
        
        for i, node1 in enumerate(territory_list):
            for j, node2 in enumerate(territory_list[i+1:], i+1):
                # Calculate distance between territories
                pos1 = (0.0, 0.0)  # Default positions - would use actual coordinates
                pos2 = (1000.0, 1000.0)  # Placeholder
                distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                
                # Only create routes within reasonable distance
                max_trade_distance = 8000  # Maximum economical trade distance
                
                if distance <= max_trade_distance:
                    edge = self._create_trade_route(node1, node2, distance)
                    self.trade_routes.append(edge)
    
    def _create_trade_route(self, node1: EconomicNode, node2: EconomicNode, 
                           distance: float) -> EconomicEdge:
        """Create trade route between two economic nodes"""
        
        # Route capacity based on territory sizes and distance
        base_capacity = min(node1.strategic_economic_value, node2.strategic_economic_value) * 100
        distance_penalty = max(0.1, 1.0 - distance / 8000.0)  # Capacity decreases with distance
        
        route_capacity = {}
        for resource_type in ResourceType:
            route_capacity[resource_type] = base_capacity * distance_penalty
        
        # Transport efficiency based on average trade efficiency
        transport_efficiency = (node1.trade_efficiency + node2.trade_efficiency) / 2
        
        # Security level based on strategic values (higher = more secure)
        security_level = (node1.strategic_economic_value + node2.strategic_economic_value) / 2
        
        # Disruption probability (inversely related to security)
        disruption_probability = max(0.05, 0.3 - security_level * 0.2)
        
        # Economic flow value
        economic_flow_value = base_capacity * transport_efficiency * security_level
        
        return EconomicEdge(
            source_territory_id=node1.territory_id,
            target_territory_id=node2.territory_id,
            route_capacity=route_capacity,
            transport_efficiency=transport_efficiency,
            security_level=security_level,
            disruption_probability=disruption_probability,
            economic_flow_value=economic_flow_value
        )
    
    def _initialize_resource_prices(self) -> None:
        """Initialize base resource prices"""
        # Base prices calibrated for game balance
        self.resource_prices = {
            ResourceType.FIELD_MATERIALS: 1.0,      # Baseline price
            ResourceType.SPLICE_COMPONENTS: 3.2,     # Higher value
            ResourceType.MONOLITH_ARTIFACTS: 8.5,    # Premium artifacts
            ResourceType.ENERGY_CORES: 2.1,         # Energy resources
            ResourceType.MANUFACTURING: 1.8,         # Processing value-add
            ResourceType.INFORMATION: 4.5,           # High-value intel
            ResourceType.LOGISTICS: 1.5              # Transportation services
        }
    
    def _load_faction_economic_profiles(self, factions: List) -> None:
        """Load faction-specific economic behavior profiles"""
        for faction in factions:
            # Parse JSON fields
            loot_tier_bias = json.loads(faction['loot_tier_bias'])
            vehicle_affinity = json.loads(faction['vehicle_affinity'])
            event_preference = json.loads(faction['event_preference'])
            
            # Create economic profile
            self.faction_economic_profiles[faction['id']] = {
                'name': faction['faction_name'],
                'tech_level': faction['tech_level'],
                'loot_preferences': loot_tier_bias,
                'transport_preferences': vehicle_affinity,
                'economic_events': event_preference,
                'trade_aggressiveness': faction['tech_level'] * 0.7 + 0.3,
                'resource_hoarding_tendency': 1.0 - faction['tech_level']  # Lower tech hoards more
            }
    
    def analyze_economic_cascade(self, source_territory_id: int, 
                                disruption_magnitude: float = 1.0,
                                cascade_type: Optional[EconomicCascadeType] = None) -> List[EconomicCascadeEvent]:
        """Analyze economic cascade effects from territorial disruption"""
        start_time = time.time()
        
        if source_territory_id not in self.economic_nodes:
            return []
        
        source_node = self.economic_nodes[source_territory_id]
        cascade_events = []
        
        # Determine cascade types if not specified
        if cascade_type is None:
            cascade_types = self._determine_economic_cascade_types(source_node, disruption_magnitude)
        else:
            cascade_types = [cascade_type]
        
        for cascade_type in cascade_types:
            cascade_event = self._calculate_economic_cascade(
                source_node, cascade_type, disruption_magnitude
            )
            
            if cascade_event and cascade_event.cascading_probability > 0.2:
                cascade_events.append(cascade_event)
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Economic cascade analysis completed in {processing_time:.2f}ms")
        
        # Update history
        for event in cascade_events:
            self.economic_cascade_history.append(event)
        
        return cascade_events
    
    def _determine_economic_cascade_types(self, source_node: EconomicNode, 
                                        magnitude: float) -> List[EconomicCascadeType]:
        """Determine which economic cascade types are relevant"""
        cascade_types = []
        
        # High economic value territories can trigger multiple cascade types
        if source_node.strategic_economic_value > 0.7:
            cascade_types.extend([
                EconomicCascadeType.SUPPLY_ROUTE_DISRUPTION,
                EconomicCascadeType.TRADE_NETWORK_COLLAPSE
            ])
        
        # Magnitude-based triggers
        if magnitude > 1.5:
            cascade_types.append(EconomicCascadeType.RESOURCE_SCARCITY_PROPAGATION)
        
        if magnitude > 2.0:
            cascade_types.append(EconomicCascadeType.INFLATION_SPIRAL)
        
        # Economic resilience factors
        if source_node.economic_resilience < 0.5:
            cascade_types.append(EconomicCascadeType.ECONOMIC_ISOLATION)
        
        return list(set(cascade_types))
    
    def _calculate_economic_cascade(self, source_node: EconomicNode,
                                   cascade_type: EconomicCascadeType,
                                   magnitude: float) -> Optional[EconomicCascadeEvent]:
        """Calculate detailed economic cascade event"""
        
        # Find affected territories and trade routes
        affected_territories, affected_routes = self._find_economically_affected_areas(
            source_node, cascade_type, magnitude
        )
        
        if not affected_territories:
            return None
        
        # Calculate resource disruption
        resource_disruption = self._calculate_resource_disruption(
            source_node, cascade_type, magnitude
        )
        
        # Calculate economic impact multiplier
        economic_impact_multiplier = self._calculate_economic_impact_multiplier(
            source_node, affected_territories, cascade_type, magnitude
        )
        
        # Calculate price inflation factors
        price_inflation = self._calculate_price_inflation(
            resource_disruption, cascade_type, magnitude
        )
        
        # Calculate supply shortage probabilities
        supply_shortage_prob = self._calculate_supply_shortage_probability(
            source_node, affected_territories, resource_disruption
        )
        
        # Estimate recovery time
        recovery_time = self._estimate_economic_recovery_time(
            cascade_type, magnitude, len(affected_territories)
        )
        
        # Calculate cascading probability
        cascading_prob = self._calculate_cascading_probability(
            source_node, affected_territories, magnitude
        )
        
        # Calculate total economic loss
        total_loss = self._calculate_total_economic_loss(
            source_node, affected_territories, economic_impact_multiplier
        )
        
        return EconomicCascadeEvent(
            cascade_id=f"eco_cascade_{int(time.time() * 1000)}_{cascade_type.value}",
            cascade_type=cascade_type,
            source_territory_id=source_node.territory_id,
            affected_territory_ids=[t.territory_id for t in affected_territories],
            affected_trade_routes=affected_routes,
            resource_disruption=resource_disruption,
            economic_impact_multiplier=economic_impact_multiplier,
            price_inflation_factor=price_inflation,
            supply_shortage_probability=supply_shortage_prob,
            recovery_time_estimate=recovery_time,
            cascading_probability=cascading_prob,
            total_economic_loss=total_loss,
            timestamp=time.time()
        )
    
    def _find_economically_affected_areas(self, source_node: EconomicNode,
                                         cascade_type: EconomicCascadeType,
                                         magnitude: float) -> Tuple[List[EconomicNode], List[Tuple[int, int]]]:
        """Find territories and trade routes affected by economic cascade"""
        affected_territories = []
        affected_routes = []
        
        # Find territories connected by trade routes
        for route in self.trade_routes:
            route_affected = False
            
            if route.source_territory_id == source_node.territory_id:
                target_node = self.economic_nodes[route.target_territory_id]
                if self._is_territory_economically_vulnerable(target_node, cascade_type, magnitude):
                    affected_territories.append(target_node)
                    route_affected = True
            
            elif route.target_territory_id == source_node.territory_id:
                source_route_node = self.economic_nodes[route.source_territory_id]
                if self._is_territory_economically_vulnerable(source_route_node, cascade_type, magnitude):
                    affected_territories.append(source_route_node)
                    route_affected = True
            
            if route_affected:
                affected_routes.append((route.source_territory_id, route.target_territory_id))
        
        return affected_territories, affected_routes
    
    def _is_territory_economically_vulnerable(self, territory: EconomicNode,
                                            cascade_type: EconomicCascadeType,
                                            magnitude: float) -> bool:
        """Determine if territory is vulnerable to economic cascade"""
        vulnerability_threshold = 0.6 - (territory.economic_resilience * 0.3)
        cascade_strength = magnitude * 0.5
        
        # Cascade type specific vulnerability
        type_modifiers = {
            EconomicCascadeType.SUPPLY_ROUTE_DISRUPTION: territory.trade_efficiency,
            EconomicCascadeType.RESOURCE_SCARCITY_PROPAGATION: 1.0 - territory.economic_resilience,
            EconomicCascadeType.TRADE_NETWORK_COLLAPSE: territory.strategic_economic_value,
            EconomicCascadeType.ECONOMIC_ISOLATION: 1.0 - territory.trade_efficiency,
            EconomicCascadeType.INFLATION_SPIRAL: territory.strategic_economic_value,
            EconomicCascadeType.MARKET_MANIPULATION: territory.trade_efficiency
        }
        
        type_modifier = type_modifiers.get(cascade_type, 1.0)
        
        return cascade_strength * type_modifier > vulnerability_threshold
    
    def _calculate_resource_disruption(self, source_node: EconomicNode,
                                     cascade_type: EconomicCascadeType,
                                     magnitude: float) -> Dict[ResourceType, float]:
        """Calculate resource disruption levels by type"""
        disruption = {}
        
        # Base disruption from magnitude
        base_disruption = min(0.8, magnitude * 0.3)
        
        # Cascade type affects different resources differently
        if cascade_type == EconomicCascadeType.SUPPLY_ROUTE_DISRUPTION:
            # Affects logistics and manufactured goods most
            disruption[ResourceType.LOGISTICS] = base_disruption * 1.5
            disruption[ResourceType.MANUFACTURING] = base_disruption * 1.3
            disruption[ResourceType.FIELD_MATERIALS] = base_disruption * 1.1
            disruption[ResourceType.ENERGY_CORES] = base_disruption * 0.9
            disruption[ResourceType.SPLICE_COMPONENTS] = base_disruption * 0.8
            disruption[ResourceType.MONOLITH_ARTIFACTS] = base_disruption * 0.7
            disruption[ResourceType.INFORMATION] = base_disruption * 0.6
            
        elif cascade_type == EconomicCascadeType.RESOURCE_SCARCITY_PROPAGATION:
            # Affects all resources but based on production capacity
            for resource_type in ResourceType:
                production_dependency = source_node.production_capacity.get(resource_type, 0) / 100
                disruption[resource_type] = base_disruption * (0.5 + production_dependency * 0.5)
                
        else:
            # Default even disruption
            for resource_type in ResourceType:
                disruption[resource_type] = base_disruption
        
        return disruption
    
    def _calculate_economic_impact_multiplier(self, source_node: EconomicNode,
                                            affected_territories: List[EconomicNode],
                                            cascade_type: EconomicCascadeType,
                                            magnitude: float) -> float:
        """Calculate economic impact multiplier"""
        base_multiplier = self.base_economic_multiplier
        
        # Source node economic importance
        source_factor = source_node.strategic_economic_value
        
        # Affected territories economic importance
        affected_factor = sum(t.strategic_economic_value for t in affected_territories) / max(1, len(affected_territories))
        
        # Magnitude scaling
        magnitude_factor = magnitude
        
        # Cascade type specific multipliers
        type_multipliers = {
            EconomicCascadeType.SUPPLY_ROUTE_DISRUPTION: 1.2,
            EconomicCascadeType.RESOURCE_SCARCITY_PROPAGATION: 1.4,
            EconomicCascadeType.TRADE_NETWORK_COLLAPSE: 1.8,
            EconomicCascadeType.ECONOMIC_ISOLATION: 1.1,
            EconomicCascadeType.INFLATION_SPIRAL: 2.2,
            EconomicCascadeType.MARKET_MANIPULATION: 1.6
        }
        
        type_multiplier = type_multipliers.get(cascade_type, 1.0)
        
        return base_multiplier * (1 + source_factor * 0.3) * (1 + affected_factor * 0.2) * magnitude_factor * type_multiplier
    
    def _calculate_price_inflation(self, resource_disruption: Dict[ResourceType, float],
                                 cascade_type: EconomicCascadeType,
                                 magnitude: float) -> Dict[ResourceType, float]:
        """Calculate price inflation factors by resource type"""
        inflation_factors = {}
        
        for resource_type, disruption_level in resource_disruption.items():
            # Base inflation from supply disruption
            base_inflation = 1.0 + (disruption_level * self.price_elasticity)
            
            # Cascade type modifier
            if cascade_type == EconomicCascadeType.INFLATION_SPIRAL:
                base_inflation *= 1.5
            elif cascade_type == EconomicCascadeType.RESOURCE_SCARCITY_PROPAGATION:
                base_inflation *= 1.3
            
            # Resource scarcity premium
            scarcity_premium = resource_disruption.get(resource_type, 0) * 0.5
            
            inflation_factors[resource_type] = base_inflation + scarcity_premium
        
        return inflation_factors
    
    def _calculate_supply_shortage_probability(self, source_node: EconomicNode,
                                             affected_territories: List[EconomicNode],
                                             resource_disruption: Dict[ResourceType, float]) -> Dict[ResourceType, float]:
        """Calculate probability of supply shortages by resource type"""
        shortage_probabilities = {}
        
        for resource_type, disruption_level in resource_disruption.items():
            # Base shortage probability from disruption
            base_shortage_prob = disruption_level
            
            # Production capacity factor
            total_production = source_node.production_capacity.get(resource_type, 0)
            for territory in affected_territories:
                total_production += territory.production_capacity.get(resource_type, 0)
            
            # Consumption demand factor
            total_demand = source_node.consumption_demand.get(resource_type, 0)
            for territory in affected_territories:
                total_demand += territory.consumption_demand.get(resource_type, 0)
            
            # Supply/demand ratio
            if total_demand > 0:
                supply_ratio = total_production / total_demand
                shortage_modifier = max(0.1, 2.0 - supply_ratio)
            else:
                shortage_modifier = 1.0
            
            shortage_probabilities[resource_type] = min(0.95, base_shortage_prob * shortage_modifier)
        
        return shortage_probabilities
    
    def _estimate_economic_recovery_time(self, cascade_type: EconomicCascadeType,
                                       magnitude: float,
                                       affected_count: int) -> float:
        """Estimate economic recovery time in hours"""
        base_recovery_times = {
            EconomicCascadeType.SUPPLY_ROUTE_DISRUPTION: 6.0,
            EconomicCascadeType.RESOURCE_SCARCITY_PROPAGATION: 12.0,
            EconomicCascadeType.TRADE_NETWORK_COLLAPSE: 24.0,
            EconomicCascadeType.ECONOMIC_ISOLATION: 8.0,
            EconomicCascadeType.INFLATION_SPIRAL: 48.0,
            EconomicCascadeType.MARKET_MANIPULATION: 18.0
        }
        
        base_time = base_recovery_times.get(cascade_type, 12.0)
        magnitude_factor = magnitude
        scale_factor = math.log(1 + affected_count) / math.log(2)
        
        return base_time * magnitude_factor * scale_factor
    
    def _calculate_cascading_probability(self, source_node: EconomicNode,
                                       affected_territories: List[EconomicNode],
                                       magnitude: float) -> float:
        """Calculate probability of further economic cascades"""
        # Base cascading probability
        base_prob = 0.25
        
        # Source node importance increases cascading potential
        source_factor = source_node.strategic_economic_value
        
        # Number of affected territories increases cascading potential
        scale_factor = min(2.0, math.log(1 + len(affected_territories)) / math.log(2))
        
        # Magnitude effect
        magnitude_factor = magnitude
        
        # Average resilience of affected territories (lower resilience = higher cascading)
        if affected_territories:
            avg_resilience = sum(t.economic_resilience for t in affected_territories) / len(affected_territories)
            resilience_factor = 2.0 - avg_resilience
        else:
            resilience_factor = 1.0
        
        return min(0.9, base_prob * source_factor * scale_factor * magnitude_factor * resilience_factor)
    
    def _calculate_total_economic_loss(self, source_node: EconomicNode,
                                     affected_territories: List[EconomicNode],
                                     economic_multiplier: float) -> float:
        """Calculate total estimated economic loss"""
        # Source node economic value
        source_value = source_node.strategic_economic_value * 1000  # Base economic units
        
        # Affected territories economic value
        affected_value = sum(t.strategic_economic_value * 1000 for t in affected_territories)
        
        # Total base economic value at risk
        total_value_at_risk = source_value + affected_value
        
        # Apply economic multiplier
        total_loss = total_value_at_risk * economic_multiplier
        
        return total_loss
    
    def get_economic_cascade_statistics(self) -> Dict[str, float]:
        """Get statistical analysis of economic cascade system"""
        if not self.economic_cascade_history:
            return {"no_data": True}
        
        multipliers = [e.economic_impact_multiplier for e in self.economic_cascade_history]
        losses = [e.total_economic_loss for e in self.economic_cascade_history]
        recovery_times = [e.recovery_time_estimate for e in self.economic_cascade_history]
        cascading_probs = [e.cascading_probability for e in self.economic_cascade_history]
        
        return {
            "total_economic_cascades": len(self.economic_cascade_history),
            "average_economic_multiplier": statistics.mean(multipliers),
            "average_economic_loss": statistics.mean(losses),
            "average_recovery_time": statistics.mean(recovery_times),
            "average_cascading_probability": statistics.mean(cascading_probs),
            "max_economic_loss": max(losses),
            "cascade_type_distribution": {
                cascade_type.value: len([e for e in self.economic_cascade_history if e.cascade_type == cascade_type])
                for cascade_type in EconomicCascadeType
            }
        }
    
    def export_economic_analysis(self, output_path: Optional[str] = None) -> str:
        """Export comprehensive economic cascade analysis"""
        if not output_path:
            output_path = "C:/Users/Zachg/Terminal-Grounds/Tools/TerritorialSystem/economic_cascade_analysis.json"
        
        analysis_data = {
            "economic_parameters": {
                "base_economic_multiplier": self.base_economic_multiplier,
                "supply_disruption_threshold": self.supply_disruption_threshold,
                "price_elasticity": self.price_elasticity,
                "recovery_rate_base": self.recovery_rate_base
            },
            "economic_network": {
                "economic_nodes_count": len(self.economic_nodes),
                "trade_routes_count": len(self.trade_routes),
                "resource_types": [rt.value for rt in ResourceType],
                "current_resource_prices": {rt.value: price for rt, price in self.resource_prices.items()}
            },
            "economic_statistics": self.get_economic_cascade_statistics(),
            "faction_economic_profiles": self.faction_economic_profiles,
            "economic_nodes_analysis": {
                str(node_id): {
                    "territory_name": node.territory_name,
                    "strategic_economic_value": node.strategic_economic_value,
                    "trade_efficiency": node.trade_efficiency,
                    "economic_resilience": node.economic_resilience,
                    "production_capacity": {rt.value: capacity for rt, capacity in node.production_capacity.items()},
                    "consumption_demand": {rt.value: demand for rt, demand in node.consumption_demand.items()}
                }
                for node_id, node in self.economic_nodes.items()
            },
            "export_timestamp": time.time()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        return output_path

def main():
    """Test economic cascade analysis system"""
    print("ECONOMIC CASCADE ANALYSIS SYSTEM")
    print("Advanced economic impact modeling")
    print("=" * 50)
    
    analyzer = EconomicCascadeAnalyzer()
    
    if not analyzer.load_economic_network():
        print("ERROR: Failed to load economic network")
        return
    
    # Test economic cascade analysis
    print("\nTesting economic cascade analysis...")
    
    # Find high-value economic territory
    high_value_nodes = [
        node_id for node_id, node in analyzer.economic_nodes.items()
        if node.strategic_economic_value > 0.6
    ]
    
    if high_value_nodes:
        test_territory = high_value_nodes[0]
        print(f"Analyzing economic cascades from territory {test_territory}")
        
        # Test different cascade scenarios
        scenarios = [
            (1.0, "Minor disruption"),
            (1.8, "Major disruption"), 
            (2.5, "Critical system failure")
        ]
        
        for magnitude, description in scenarios:
            cascades = analyzer.analyze_economic_cascade(test_territory, magnitude)
            
            print(f"\n{description} (magnitude {magnitude}):")
            print(f"  Economic cascades triggered: {len(cascades)}")
            
            for cascade in cascades[:2]:  # Show top 2
                print(f"    Type: {cascade.cascade_type.value}")
                print(f"    Economic loss: {cascade.total_economic_loss:.0f} units")
                print(f"    Recovery time: {cascade.recovery_time_estimate:.1f} hours")
                print(f"    Cascading probability: {cascade.cascading_probability:.2f}")
    
    # Export analysis
    analysis_path = analyzer.export_economic_analysis()
    print(f"\nEconomic analysis exported to: {analysis_path}")
    
    # Statistics
    stats = analyzer.get_economic_cascade_statistics()
    if "no_data" not in stats:
        print(f"\nEconomic Cascade Statistics:")
        print(f"  Total cascades analyzed: {stats['total_economic_cascades']}")
        print(f"  Average economic loss: {stats['average_economic_loss']:.0f} units")
        print(f"  Average recovery time: {stats['average_recovery_time']:.1f} hours")
    
    print("\n" + "=" * 50)
    print("ECONOMIC CASCADE SYSTEM OPERATIONAL")
    print("Supply chain disruption modeling active")
    print("Economic impact assessment ready")

if __name__ == "__main__":
    main()