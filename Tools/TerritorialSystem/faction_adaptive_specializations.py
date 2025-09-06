#!/usr/bin/env python3
"""
Faction-Specific Adaptive Behavior Specializations
Performance Engineer Implementation - Advanced AI behavior patterns per faction

Implements lore-accurate adaptive behaviors that evolve based on territorial success/failure
while maintaining high performance for 100+ concurrent players.
"""

import json
import time
import random
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

class SpecializationType(Enum):
    ECONOMIC_WARFARE = "economic_warfare"
    GUERRILLA_TACTICS = "guerrilla_tactics"
    TECHNOLOGICAL_SUPERIORITY = "technological_superiority"
    COALITION_BUILDING = "coalition_building"
    RESOURCE_HOARDING = "resource_hoarding"
    INFORMATION_WARFARE = "information_warfare"
    DEFENSIVE_MASTERY = "defensive_mastery"

@dataclass
class AdaptiveSpecialization:
    """Faction-specific adaptive behavior specialization"""
    specialization_type: SpecializationType
    effectiveness: float  # 0.0 to 1.0
    learning_rate: float
    activation_threshold: float  # Situation threshold to activate this specialization
    success_history: deque = field(default_factory=lambda: deque(maxlen=20))
    adaptation_triggers: List[str] = field(default_factory=list)
    
class FactionSpecializations:
    """Faction-specific adaptive behavior implementations"""
    
    @staticmethod
    def get_directorate_specializations() -> Dict[SpecializationType, AdaptiveSpecialization]:
        """Sky Bastion Directorate - Corporate military efficiency specializations"""
        return {
            SpecializationType.ECONOMIC_WARFARE: AdaptiveSpecialization(
                specialization_type=SpecializationType.ECONOMIC_WARFARE,
                effectiveness=0.8,
                learning_rate=0.12,
                activation_threshold=0.6,
                adaptation_triggers=["resource_advantage", "economic_pressure", "trade_route_control"]
            ),
            SpecializationType.TECHNOLOGICAL_SUPERIORITY: AdaptiveSpecialization(
                specialization_type=SpecializationType.TECHNOLOGICAL_SUPERIORITY,
                effectiveness=0.7,
                learning_rate=0.08,
                activation_threshold=0.5,
                adaptation_triggers=["tech_facility_control", "high_value_targets", "innovation_pressure"]
            ),
            SpecializationType.COALITION_BUILDING: AdaptiveSpecialization(
                specialization_type=SpecializationType.COALITION_BUILDING,
                effectiveness=0.4,
                learning_rate=0.06,
                activation_threshold=0.7,
                adaptation_triggers=["multiple_threats", "resource_sharing_opportunities"]
            )
        }
    
    @staticmethod 
    def get_iron_scavengers_specializations() -> Dict[SpecializationType, AdaptiveSpecialization]:
        """Iron Scavengers - Opportunistic resource acquisition specializations"""
        return {
            SpecializationType.RESOURCE_HOARDING: AdaptiveSpecialization(
                specialization_type=SpecializationType.RESOURCE_HOARDING,
                effectiveness=0.9,
                learning_rate=0.15,
                activation_threshold=0.4,
                adaptation_triggers=["scarcity_detected", "resource_opportunity", "stockpile_depletion"]
            ),
            SpecializationType.GUERRILLA_TACTICS: AdaptiveSpecialization(
                specialization_type=SpecializationType.GUERRILLA_TACTICS,
                effectiveness=0.7,
                learning_rate=0.18,
                activation_threshold=0.5,
                adaptation_triggers=["outnumbered", "hit_and_run_success", "asymmetric_advantage"]
            ),
            SpecializationType.ECONOMIC_WARFARE: AdaptiveSpecialization(
                specialization_type=SpecializationType.ECONOMIC_WARFARE,
                effectiveness=0.6,
                learning_rate=0.10,
                activation_threshold=0.6,
                adaptation_triggers=["disruption_opportunity", "competitor_weakness"]
            )
        }
    
    @staticmethod
    def get_free77_specializations() -> Dict[SpecializationType, AdaptiveSpecialization]:
        """The Seventy-Seven - Elite mercenary pragmatism specializations"""
        return {
            SpecializationType.COALITION_BUILDING: AdaptiveSpecialization(
                specialization_type=SpecializationType.COALITION_BUILDING,
                effectiveness=0.85,
                learning_rate=0.14,
                activation_threshold=0.4,
                adaptation_triggers=["mutual_benefit", "contract_opportunity", "threat_sharing"]
            ),
            SpecializationType.INFORMATION_WARFARE: AdaptiveSpecialization(
                specialization_type=SpecializationType.INFORMATION_WARFARE,
                effectiveness=0.7,
                learning_rate=0.12,
                activation_threshold=0.5,
                adaptation_triggers=["intelligence_gap", "strategic_advantage", "enemy_weakness_detected"]
            ),
            SpecializationType.TECHNOLOGICAL_SUPERIORITY: AdaptiveSpecialization(
                specialization_type=SpecializationType.TECHNOLOGICAL_SUPERIORITY,
                effectiveness=0.6,
                learning_rate=0.08,
                activation_threshold=0.6,
                adaptation_triggers=["equipment_advantage", "tech_facility_access"]
            )
        }
    
    @staticmethod
    def get_corporate_hegemony_specializations() -> Dict[SpecializationType, AdaptiveSpecialization]:
        """Corporate Hegemony - High-tech dominance specializations"""
        return {
            SpecializationType.TECHNOLOGICAL_SUPERIORITY: AdaptiveSpecialization(
                specialization_type=SpecializationType.TECHNOLOGICAL_SUPERIORITY,
                effectiveness=0.95,
                learning_rate=0.10,
                activation_threshold=0.3,
                adaptation_triggers=["research_breakthrough", "tech_monopoly", "innovation_lead"]
            ),
            SpecializationType.INFORMATION_WARFARE: AdaptiveSpecialization(
                specialization_type=SpecializationType.INFORMATION_WARFARE,
                effectiveness=0.8,
                learning_rate=0.11,
                activation_threshold=0.4,
                adaptation_triggers=["data_advantage", "surveillance_network", "predictive_modeling"]
            ),
            SpecializationType.ECONOMIC_WARFARE: AdaptiveSpecialization(
                specialization_type=SpecializationType.ECONOMIC_WARFARE,
                effectiveness=0.7,
                learning_rate=0.09,
                activation_threshold=0.5,
                adaptation_triggers=["market_manipulation", "resource_control", "competitor_pressure"]
            )
        }
    
    @staticmethod
    def get_nomad_clans_specializations() -> Dict[SpecializationType, AdaptiveSpecialization]:
        """Nomad Clans - Mobile survival specializations"""
        return {
            SpecializationType.GUERRILLA_TACTICS: AdaptiveSpecialization(
                specialization_type=SpecializationType.GUERRILLA_TACTICS,
                effectiveness=0.85,
                learning_rate=0.16,
                activation_threshold=0.4,
                adaptation_triggers=["mobility_advantage", "terrain_knowledge", "evasion_success"]
            ),
            SpecializationType.RESOURCE_HOARDING: AdaptiveSpecialization(
                specialization_type=SpecializationType.RESOURCE_HOARDING,
                effectiveness=0.8,
                learning_rate=0.14,
                activation_threshold=0.5,
                adaptation_triggers=["survival_pressure", "migration_preparation", "scarcity_adaptation"]
            ),
            SpecializationType.DEFENSIVE_MASTERY: AdaptiveSpecialization(
                specialization_type=SpecializationType.DEFENSIVE_MASTERY,
                effectiveness=0.6,
                learning_rate=0.10,
                activation_threshold=0.6,
                adaptation_triggers=["settlement_threat", "caravan_protection", "safe_zone_establishment"]
            )
        }
    
    @staticmethod
    def get_archive_keepers_specializations() -> Dict[SpecializationType, AdaptiveSpecialization]:
        """Archive Keepers - Knowledge preservation specializations"""
        return {
            SpecializationType.INFORMATION_WARFARE: AdaptiveSpecialization(
                specialization_type=SpecializationType.INFORMATION_WARFARE,
                effectiveness=0.9,
                learning_rate=0.13,
                activation_threshold=0.3,
                adaptation_triggers=["knowledge_advantage", "information_asymmetry", "data_collection"]
            ),
            SpecializationType.TECHNOLOGICAL_SUPERIORITY: AdaptiveSpecialization(
                specialization_type=SpecializationType.TECHNOLOGICAL_SUPERIORITY,
                effectiveness=0.75,
                learning_rate=0.11,
                activation_threshold=0.4,
                adaptation_triggers=["research_facility_access", "innovation_opportunity", "tech_preservation"]
            ),
            SpecializationType.DEFENSIVE_MASTERY: AdaptiveSpecialization(
                specialization_type=SpecializationType.DEFENSIVE_MASTERY,
                effectiveness=0.7,
                learning_rate=0.09,
                activation_threshold=0.5,
                adaptation_triggers=["archive_protection", "knowledge_vault_security", "preservation_priority"]
            )
        }
    
    @staticmethod
    def get_civic_wardens_specializations() -> Dict[SpecializationType, AdaptiveSpecialization]:
        """Civic Wardens - Community protection specializations"""
        return {
            SpecializationType.DEFENSIVE_MASTERY: AdaptiveSpecialization(
                specialization_type=SpecializationType.DEFENSIVE_MASTERY,
                effectiveness=0.9,
                learning_rate=0.12,
                activation_threshold=0.3,
                adaptation_triggers=["community_threat", "civilian_protection", "infrastructure_defense"]
            ),
            SpecializationType.COALITION_BUILDING: AdaptiveSpecialization(
                specialization_type=SpecializationType.COALITION_BUILDING,
                effectiveness=0.85,
                learning_rate=0.15,
                activation_threshold=0.4,
                adaptation_triggers=["mutual_aid", "community_cooperation", "shared_defense"]
            ),
            SpecializationType.ECONOMIC_WARFARE: AdaptiveSpecialization(
                specialization_type=SpecializationType.ECONOMIC_WARFARE,
                effectiveness=0.5,
                learning_rate=0.07,
                activation_threshold=0.7,
                adaptation_triggers=["resource_sharing", "community_economics", "cooperative_advantage"]
            )
        }

class FactionAdaptiveBehaviorEngine:
    """
    Advanced faction behavior engine with lore-accurate adaptive specializations
    Optimized for performance with 100+ concurrent players
    """
    
    def __init__(self):
        self.faction_specializations = self._initialize_faction_specializations()
        self.specialization_activation_history = defaultdict(lambda: deque(maxlen=100))
        self.cross_faction_learning = defaultdict(lambda: defaultdict(float))  # Learning from other factions
        self.economic_integration_data = {}
        
        print("Faction Adaptive Behavior Engine initialized")
        print(f"Loaded specializations for {len(self.faction_specializations)} factions")
        
    def _initialize_faction_specializations(self) -> Dict[int, Dict[SpecializationType, AdaptiveSpecialization]]:
        """Initialize all faction specializations"""
        return {
            1: FactionSpecializations.get_directorate_specializations(),        # Sky Bastion Directorate
            2: FactionSpecializations.get_iron_scavengers_specializations(),    # Iron Scavengers  
            3: FactionSpecializations.get_free77_specializations(),             # The Seventy-Seven
            4: FactionSpecializations.get_corporate_hegemony_specializations(), # Corporate Hegemony
            5: FactionSpecializations.get_nomad_clans_specializations(),        # Nomad Clans
            6: FactionSpecializations.get_archive_keepers_specializations(),    # Archive Keepers
            7: FactionSpecializations.get_civic_wardens_specializations()       # Civic Wardens
        }
        
    def evaluate_specialization_activation(self, faction_id: int, territorial_context: Dict, 
                                         economic_context: Dict = None) -> List[Tuple[SpecializationType, float]]:
        """Evaluate which specializations should activate based on current context"""
        if faction_id not in self.faction_specializations:
            return []
            
        active_specializations = []
        faction_specs = self.faction_specializations[faction_id]
        
        for spec_type, specialization in faction_specs.items():
            activation_score = self._calculate_activation_score(
                faction_id, specialization, territorial_context, economic_context
            )
            
            if activation_score >= specialization.activation_threshold:
                active_specializations.append((spec_type, activation_score))
                
        # Sort by activation score
        active_specializations.sort(key=lambda x: x[1], reverse=True)
        return active_specializations
        
    def _calculate_activation_score(self, faction_id: int, specialization: AdaptiveSpecialization,
                                   territorial_context: Dict, economic_context: Dict = None) -> float:
        """Calculate activation score for a specialization based on context"""
        base_score = specialization.effectiveness * 0.3
        
        # Context-based scoring
        context_score = 0.0
        
        if specialization.specialization_type == SpecializationType.ECONOMIC_WARFARE:
            context_score += self._score_economic_warfare_context(faction_id, territorial_context, economic_context)
            
        elif specialization.specialization_type == SpecializationType.GUERRILLA_TACTICS:
            context_score += self._score_guerrilla_tactics_context(faction_id, territorial_context)
            
        elif specialization.specialization_type == SpecializationType.TECHNOLOGICAL_SUPERIORITY:
            context_score += self._score_tech_superiority_context(faction_id, territorial_context)
            
        elif specialization.specialization_type == SpecializationType.COALITION_BUILDING:
            context_score += self._score_coalition_building_context(faction_id, territorial_context)
            
        elif specialization.specialization_type == SpecializationType.RESOURCE_HOARDING:
            context_score += self._score_resource_hoarding_context(faction_id, territorial_context, economic_context)
            
        elif specialization.specialization_type == SpecializationType.INFORMATION_WARFARE:
            context_score += self._score_information_warfare_context(faction_id, territorial_context)
            
        elif specialization.specialization_type == SpecializationType.DEFENSIVE_MASTERY:
            context_score += self._score_defensive_mastery_context(faction_id, territorial_context)
            
        # Historical success modifier
        if specialization.success_history:
            historical_success = statistics.mean(specialization.success_history)
            context_score *= (0.7 + historical_success * 0.6)  # 0.7 to 1.3 multiplier
            
        return min(1.0, base_score + context_score)
        
    def _score_economic_warfare_context(self, faction_id: int, territorial_context: Dict, 
                                       economic_context: Dict = None) -> float:
        """Score economic warfare specialization activation"""
        score = 0.0
        
        # Territory-based economic indicators
        our_territories = [t for t in territorial_context['territories'] 
                          if t['current_controller_faction_id'] == faction_id]
        our_economic_value = sum(t['strategic_value'] for t in our_territories if t['strategic_value'] >= 6)
        
        # Economic pressure from competitors
        competitor_economic_power = 0
        for territory in territorial_context['territories']:
            controller = territory['current_controller_faction_id']
            if controller and controller != faction_id and territory['strategic_value'] >= 6:
                competitor_economic_power += territory['strategic_value']
                
        if competitor_economic_power > our_economic_value * 1.2:
            score += 0.4  # Under economic pressure
            
        # Resource control opportunities
        high_value_uncontrolled = [t for t in territorial_context['territories'] 
                                  if t['strategic_value'] >= 8 and not t['current_controller_faction_id']]
        if high_value_uncontrolled:
            score += min(0.3, len(high_value_uncontrolled) * 0.1)
            
        # Economic context integration
        if economic_context:
            convoy_integrity = economic_context.get('convoy_integrity', 0.5)
            if convoy_integrity < 0.4:  # Economic disruption detected
                score += 0.3
                
        return score
        
    def _score_guerrilla_tactics_context(self, faction_id: int, territorial_context: Dict) -> float:
        """Score guerrilla tactics specialization activation"""
        score = 0.0
        
        our_territories = [t for t in territorial_context['territories'] 
                          if t['current_controller_faction_id'] == faction_id]
        our_territory_count = len(our_territories)
        total_territories = len(territorial_context['territories'])
        
        # Underdog situation favors guerrilla tactics
        territory_ratio = our_territory_count / max(total_territories, 1)
        if territory_ratio < 0.3:
            score += 0.5  # Significant underdog
        elif territory_ratio < 0.5:
            score += 0.3  # Minor underdog
            
        # Multiple stronger opponents
        stronger_opponents = 0
        for other_faction_id in range(1, 8):
            if other_faction_id == faction_id:
                continue
                
            their_territories = [t for t in territorial_context['territories'] 
                               if t['current_controller_faction_id'] == other_faction_id]
            their_power = sum(t['strategic_value'] for t in their_territories)
            our_power = sum(t['strategic_value'] for t in our_territories)
            
            if their_power > our_power * 1.3:
                stronger_opponents += 1
                
        if stronger_opponents >= 2:
            score += 0.4
        elif stronger_opponents == 1:
            score += 0.2
            
        return score
        
    def _score_tech_superiority_context(self, faction_id: int, territorial_context: Dict) -> float:
        """Score technological superiority specialization activation"""
        score = 0.0
        
        # Control of research/tech facilities
        tech_facilities = [t for t in territorial_context['territories']
                          if any(keyword in t['territory_name'].lower() 
                                for keyword in ['research', 'tech', 'laboratory', 'facility', 'iez'])]
        
        our_tech_facilities = [t for t in tech_facilities 
                              if t['current_controller_faction_id'] == faction_id]
        
        if our_tech_facilities:
            score += min(0.4, len(our_tech_facilities) * 0.15)
            
        # Opportunity to capture tech facilities
        available_tech_facilities = [t for t in tech_facilities 
                                   if not t['current_controller_faction_id'] or t['contested']]
        
        if available_tech_facilities:
            score += min(0.3, len(available_tech_facilities) * 0.1)
            
        return score
        
    def _score_coalition_building_context(self, faction_id: int, territorial_context: Dict) -> float:
        """Score coalition building specialization activation"""
        score = 0.0
        
        # Multiple strong competitors favor coalition building
        competitor_strength = {}
        our_territories = [t for t in territorial_context['territories'] 
                          if t['current_controller_faction_id'] == faction_id]
        our_power = sum(t['strategic_value'] for t in our_territories)
        
        for other_faction_id in range(1, 8):
            if other_faction_id == faction_id:
                continue
                
            their_territories = [t for t in territorial_context['territories'] 
                               if t['current_controller_faction_id'] == other_faction_id]
            their_power = sum(t['strategic_value'] for t in their_territories)
            
            if their_power > 0:
                competitor_strength[other_faction_id] = their_power
                
        # If there are multiple competitors stronger than us
        stronger_competitors = [fid for fid, power in competitor_strength.items() 
                              if power > our_power * 1.1]
        
        if len(stronger_competitors) >= 2:
            score += 0.5
        elif len(stronger_competitors) == 1:
            score += 0.3
            
        # Opportunity to ally against dominant faction
        if competitor_strength:
            dominant_faction_power = max(competitor_strength.values())
            if dominant_faction_power > our_power * 2.0:
                score += 0.4
                
        return score
        
    def _score_resource_hoarding_context(self, faction_id: int, territorial_context: Dict, 
                                        economic_context: Dict = None) -> float:
        """Score resource hoarding specialization activation"""
        score = 0.0
        
        # Low overall resource control triggers hoarding
        our_territories = [t for t in territorial_context['territories'] 
                          if t['current_controller_faction_id'] == faction_id]
        our_resource_value = sum(t['strategic_value'] for t in our_territories)
        
        total_resource_value = sum(t['strategic_value'] for t in territorial_context['territories'])
        our_resource_ratio = our_resource_value / max(total_resource_value, 1)
        
        if our_resource_ratio < 0.2:
            score += 0.5  # Very low resources
        elif our_resource_ratio < 0.4:
            score += 0.3  # Low resources
            
        # Economic pressure indicators
        if economic_context:
            convoy_integrity = economic_context.get('convoy_integrity', 0.5)
            if convoy_integrity < 0.3:
                score += 0.4  # Economic crisis
                
        # Resource scarcity in region
        high_value_territories = [t for t in territorial_context['territories'] 
                                 if t['strategic_value'] >= 7]
        contested_resources = sum(1 for t in high_value_territories if t['contested'])
        
        if contested_resources >= len(high_value_territories) * 0.6:
            score += 0.3  # High resource competition
            
        return score
        
    def _score_information_warfare_context(self, faction_id: int, territorial_context: Dict) -> float:
        """Score information warfare specialization activation"""
        score = 0.0
        
        # Control of information-relevant territories
        info_territories = [t for t in territorial_context['territories']
                           if any(keyword in t['territory_name'].lower() 
                                 for keyword in ['data', 'archive', 'research', 'communication', 'intel'])]
        
        our_info_control = sum(1 for t in info_territories 
                              if t['current_controller_faction_id'] == faction_id)
        
        if our_info_control > 0:
            score += min(0.4, our_info_control * 0.2)
            
        # Information asymmetry opportunities
        # (In a real implementation, this would consider actual intelligence data)
        contested_territories = sum(1 for t in territorial_context['territories'] if t['contested'])
        if contested_territories >= 3:
            score += 0.3  # Many contested areas = information advantage opportunities
            
        return score
        
    def _score_defensive_mastery_context(self, faction_id: int, territorial_context: Dict) -> float:
        """Score defensive mastery specialization activation"""
        score = 0.0
        
        # High threat level activates defensive specialization
        our_territories = [t for t in territorial_context['territories'] 
                          if t['current_controller_faction_id'] == faction_id]
        
        contested_our_territories = sum(1 for t in our_territories if t['contested'])
        if contested_our_territories > 0:
            score += min(0.5, contested_our_territories * 0.25)
            
        # Proximity to hostile factions
        threats_nearby = 0
        for our_territory in our_territories:
            for other_territory in territorial_context['territories']:
                if (other_territory['current_controller_faction_id'] and 
                    other_territory['current_controller_faction_id'] != faction_id):
                    # Simple proximity check (could be enhanced with coordinates)
                    if abs(our_territory['id'] - other_territory['id']) <= 2:
                        threats_nearby += 1
                        
        if threats_nearby > len(our_territories):
            score += 0.4  # Surrounded
        elif threats_nearby > 0:
            score += 0.2  # Some threats
            
        return score
        
    def adapt_specialization_from_outcome(self, faction_id: int, specialization_type: SpecializationType,
                                         success: bool, influence_change: int) -> None:
        """Adapt specialization based on action outcome"""
        if faction_id not in self.faction_specializations:
            return
            
        if specialization_type not in self.faction_specializations[faction_id]:
            return
            
        specialization = self.faction_specializations[faction_id][specialization_type]
        
        # Record success/failure
        specialization.success_history.append(float(success))
        
        # Adapt effectiveness based on outcome
        if success:
            # Positive reinforcement
            effectiveness_change = specialization.learning_rate * (influence_change / 100.0)
            specialization.effectiveness = min(1.0, specialization.effectiveness + effectiveness_change)
            
            # Lower activation threshold if very successful
            if influence_change > 30:
                specialization.activation_threshold *= 0.98
                
        else:
            # Negative reinforcement
            effectiveness_change = specialization.learning_rate * 0.5
            specialization.effectiveness = max(0.1, specialization.effectiveness - effectiveness_change)
            
            # Raise activation threshold if failing
            if influence_change < -20:
                specialization.activation_threshold = min(0.9, specialization.activation_threshold * 1.02)
                
        # Record activation for history
        self.specialization_activation_history[faction_id].append({
            'specialization': specialization_type.value,
            'success': success,
            'influence_change': influence_change,
            'effectiveness': specialization.effectiveness,
            'timestamp': time.time()
        })
        
    def cross_faction_learning_update(self, observer_faction_id: int, observed_faction_id: int,
                                     observed_specialization: SpecializationType, success: bool) -> None:
        """Update cross-faction learning from observing other faction's actions"""
        # Factions can learn from observing successful strategies of others
        if success and observer_faction_id != observed_faction_id:
            learning_rate = 0.05  # Lower learning rate for cross-faction learning
            
            # If we don't have this specialization, we can't learn it
            if observed_specialization not in self.faction_specializations.get(observer_faction_id, {}):
                return
                
            # Increase our own effectiveness for this specialization based on observation
            our_specialization = self.faction_specializations[observer_faction_id][observed_specialization]
            effectiveness_boost = learning_rate * random.uniform(0.5, 1.0)  # Some randomness
            our_specialization.effectiveness = min(1.0, our_specialization.effectiveness + effectiveness_boost)
            
            # Track cross-faction learning
            self.cross_faction_learning[observer_faction_id][observed_faction_id] += effectiveness_boost
            
    def integrate_economic_context(self, economic_data: Dict) -> None:
        """Integrate economic system data for better decision making"""
        self.economic_integration_data = economic_data
        
        # Adjust faction specializations based on economic conditions
        if 'convoy_integrity' in economic_data:
            convoy_integrity = economic_data['convoy_integrity']
            
            # Low convoy integrity affects resource-dependent factions more
            if convoy_integrity < 0.4:
                # Resource-focused factions adapt their strategies
                for faction_id in [2, 5]:  # Iron Scavengers, Nomad Clans
                    if faction_id in self.faction_specializations:
                        if SpecializationType.RESOURCE_HOARDING in self.faction_specializations[faction_id]:
                            spec = self.faction_specializations[faction_id][SpecializationType.RESOURCE_HOARDING]
                            spec.activation_threshold *= 0.9  # Easier to activate
                            
        if 'trust_levels' in economic_data:
            trust_data = economic_data['trust_levels']
            
            # High trust levels favor coalition building
            for faction_id, faction_trust in trust_data.items():
                if faction_id in self.faction_specializations:
                    if SpecializationType.COALITION_BUILDING in self.faction_specializations[faction_id]:
                        spec = self.faction_specializations[faction_id][SpecializationType.COALITION_BUILDING]
                        avg_trust = statistics.mean(faction_trust.values()) if faction_trust else 0.5
                        
                        if avg_trust > 0.6:
                            spec.effectiveness = min(1.0, spec.effectiveness * 1.1)
                        elif avg_trust < 0.3:
                            spec.effectiveness = max(0.1, spec.effectiveness * 0.9)
                            
    def get_faction_behavioral_summary(self, faction_id: int) -> Dict:
        """Get comprehensive behavioral summary for a faction"""
        if faction_id not in self.faction_specializations:
            return {}
            
        specializations_summary = {}
        for spec_type, spec in self.faction_specializations[faction_id].items():
            specializations_summary[spec_type.value] = {
                'effectiveness': spec.effectiveness,
                'activation_threshold': spec.activation_threshold,
                'recent_success_rate': statistics.mean(spec.success_history) if spec.success_history else 0.5,
                'adaptations_count': len(spec.success_history),
                'learning_rate': spec.learning_rate
            }
            
        return {
            'faction_id': faction_id,
            'specializations': specializations_summary,
            'activation_history': list(self.specialization_activation_history[faction_id])[-10:],  # Last 10
            'cross_faction_learning': dict(self.cross_faction_learning[faction_id]),
            'economic_adaptation_active': bool(self.economic_integration_data)
        }
        
    def export_specialization_analysis(self) -> str:
        """Export comprehensive specialization analysis"""
        analysis = {
            'faction_specializations': {},
            'cross_faction_learning': {},
            'specialization_activation_patterns': {},
            'economic_integration': self.economic_integration_data,
            'analysis_timestamp': time.time()
        }
        
        # Export faction data
        for faction_id, specializations in self.faction_specializations.items():
            faction_data = {}
            for spec_type, spec in specializations.items():
                faction_data[spec_type.value] = {
                    'effectiveness': spec.effectiveness,
                    'activation_threshold': spec.activation_threshold,
                    'learning_rate': spec.learning_rate,
                    'success_history': list(spec.success_history),
                    'adaptation_triggers': spec.adaptation_triggers
                }
            analysis['faction_specializations'][faction_id] = faction_data
            
        # Export cross-faction learning
        for observer_id, learned_from in self.cross_faction_learning.items():
            analysis['cross_faction_learning'][observer_id] = dict(learned_from)
            
        # Export activation patterns
        for faction_id, history in self.specialization_activation_history.items():
            analysis['specialization_activation_patterns'][faction_id] = list(history)[-50:]  # Last 50
            
        output_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/TerritorialSystem/faction_specialization_analysis.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
            
        return str(output_path)

if __name__ == "__main__":
    print("Faction Adaptive Behavior Engine - Specialized AI Behaviors")
    print("Performance optimized for 100+ concurrent territorial warfare")
    
    behavior_engine = FactionAdaptiveBehaviorEngine()
    
    # Demonstration of specialization system
    print("\nFaction Specializations Overview:")
    for faction_id in range(1, 8):
        summary = behavior_engine.get_faction_behavioral_summary(faction_id)
        faction_name = ["", "Sky Bastion Directorate", "Iron Scavengers", "The Seventy-Seven", 
                       "Corporate Hegemony", "Nomad Clans", "Archive Keepers", "Civic Wardens"][faction_id]
        print(f"\n{faction_name} ({faction_id}):")
        for spec_name, spec_data in summary['specializations'].items():
            print(f"  {spec_name}: {spec_data['effectiveness']:.2f} effectiveness")
            
    analysis_path = behavior_engine.export_specialization_analysis()
    print(f"\nSpecialization analysis exported to: {analysis_path}")
    print("\nFaction adaptive behavior specializations ready for integration")