# -*- coding: utf-8 -*-
"""
Terminal Grounds - Comprehensive Territorial Analytics Suite Runner
Orchestrates complete statistical modeling and data-driven analysis system

This script demonstrates the integration of all statistical modeling components:
1. Territorial resource statistical analysis
2. Advanced faction balance optimization  
3. Real-time analytics dashboard
4. Business intelligence reporting
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
import json
from datetime import datetime

class TerritorialAnalyticsSuite:
    """
    Comprehensive analytics suite orchestrator for Terminal Grounds territorial systems
    Integrates statistical modeling, balance optimization, and real-time monitoring
    """
    
    def __init__(self):
        self.suite_start_time = datetime.now()
        self.script_directory = Path(__file__).parent
        
        # Component scripts
        self.components = {
            'statistical_analysis': 'territorial_resource_statistical_analysis.py',
            'balance_optimizer': 'advanced_faction_balance_optimizer.py', 
            'realtime_dashboard': 'realtime_territorial_analytics_dashboard.py'
        }
        
        # Results storage
        self.component_results = {}
        self.executive_summary = {}
        
    def run_complete_analytics_suite(self):
        """Run the complete territorial analytics suite"""
        
        print("🚀 TERMINAL GROUNDS - COMPREHENSIVE TERRITORIAL ANALYTICS SUITE")
        print("="*80)
        print(f"Suite started at: {self.suite_start_time}")
        print(f"Components: {len(self.components)}")
        print("="*80)
        
        try:
            # Phase 1: Statistical Analysis
            print("\n📊 PHASE 1: TERRITORIAL RESOURCE STATISTICAL ANALYSIS")
            print("-" * 60)
            statistical_results = self._run_statistical_analysis()
            self.component_results['statistical_analysis'] = statistical_results
            
            # Phase 2: Balance Optimization
            print("\n⚖️  PHASE 2: ADVANCED FACTION BALANCE OPTIMIZATION") 
            print("-" * 60)
            optimization_results = self._run_balance_optimization()
            self.component_results['balance_optimization'] = optimization_results
            
            # Phase 3: Generate Comprehensive Report
            print("\n📋 PHASE 3: COMPREHENSIVE BUSINESS INTELLIGENCE REPORT")
            print("-" * 60)
            self._generate_comprehensive_report()
            
            # Phase 4: Optional Real-time Dashboard
            print("\n🌐 PHASE 4: REAL-TIME ANALYTICS DASHBOARD (OPTIONAL)")
            print("-" * 60)
            dashboard_choice = input("Start real-time dashboard server? (y/N): ").strip().lower()
            
            if dashboard_choice == 'y':
                print("Starting real-time dashboard...")
                print("Dashboard will be available at: http://localhost:5000")
                print("Press Ctrl+C to stop the dashboard when finished.")
                self._run_realtime_dashboard()
            else:
                print("Skipping real-time dashboard")
                
            # Final summary
            self._print_final_summary()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Analytics suite interrupted by user")
            return False
            
        except Exception as e:
            print(f"\n❌ Error in analytics suite: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _run_statistical_analysis(self):
        """Run territorial resource statistical analysis"""
        
        print("Executing territorial resource statistical analysis...")
        
        try:
            # Import and run statistical analysis
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "statistical_analysis", 
                self.script_directory / self.components['statistical_analysis']
            )
            
            if spec and spec.loader:
                statistical_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(statistical_module)
                
                # Run the main analysis
                if hasattr(statistical_module, 'main'):
                    results = statistical_module.main()
                    
                    if results:
                        print("✅ Statistical analysis completed successfully")
                        return self._extract_statistical_summary(results)
                    else:
                        print("⚠️  Statistical analysis returned no results")
                        return None
                else:
                    print("⚠️  Statistical analysis module has no main function")
                    return None
            else:
                print("❌ Failed to load statistical analysis module")
                return None
                
        except Exception as e:
            print(f"❌ Error in statistical analysis: {e}")
            return None
            
    def _run_balance_optimization(self):
        """Run advanced faction balance optimization"""
        
        print("Executing advanced faction balance optimization...")
        
        try:
            # Import and run balance optimizer
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "balance_optimizer",
                self.script_directory / self.components['balance_optimizer']  
            )
            
            if spec and spec.loader:
                optimizer_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(optimizer_module)
                
                # Run the optimization
                if hasattr(optimizer_module, 'main'):
                    results = optimizer_module.main()
                    
                    if results:
                        print("✅ Balance optimization completed successfully")
                        return self._extract_optimization_summary(results)
                    else:
                        print("⚠️  Balance optimization returned no results")
                        return None
                else:
                    print("⚠️  Balance optimization module has no main function")
                    return None
            else:
                print("❌ Failed to load balance optimization module")
                return None
                
        except Exception as e:
            print(f"❌ Error in balance optimization: {e}")
            return None
            
    def _run_realtime_dashboard(self):
        """Run real-time analytics dashboard"""
        
        try:
            # Import and run dashboard
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "realtime_dashboard",
                self.script_directory / self.components['realtime_dashboard']
            )
            
            if spec and spec.loader:
                dashboard_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(dashboard_module)
                
                # Run the dashboard
                if hasattr(dashboard_module, 'main'):
                    # This will run until interrupted
                    asyncio.run(dashboard_module.main())
                else:
                    print("⚠️  Dashboard module has no main function")
            else:
                print("❌ Failed to load dashboard module")
                
        except KeyboardInterrupt:
            print("\n⏹️  Dashboard stopped by user")
            
        except Exception as e:
            print(f"❌ Error in dashboard: {e}")
            
    def _extract_statistical_summary(self, results):
        """Extract key summary from statistical analysis results"""
        
        if not results:
            return None
            
        summary = {
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Extract balance analysis
            if 'balance_analysis' in results:
                balance = results['balance_analysis']
                if 'overall_balance' in balance:
                    summary['overall_balance_score'] = balance['overall_balance']['score']
                    summary['balance_status'] = balance['overall_balance']['status']
                    
            # Extract optimization results
            if 'best_configurations' in results:
                summary['optimal_configs_found'] = len(results['best_configurations'])
                
            # Extract business intelligence
            if 'business_intelligence' in results:
                bi = results['business_intelligence']
                if 'executive_summary' in bi:
                    exec_summary = bi['executive_summary']
                    summary['executive_balance_score'] = exec_summary.get('overall_balance_score', 0)
                    summary['executive_status'] = exec_summary.get('balance_status', 'UNKNOWN')
                    
        except Exception as e:
            print(f"⚠️  Warning: Error extracting statistical summary: {e}")
            summary['extraction_error'] = str(e)
            
        return summary
        
    def _extract_optimization_summary(self, results):
        """Extract key summary from optimization results"""
        
        if not results:
            return None
            
        summary = {
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Extract optimization results
            if 'optimization_results' in results:
                opt_results = results['optimization_results']
                summary['optimization_success'] = opt_results.get('optimization_success', False)
                summary['objective_value'] = opt_results.get('objective_value', 0)
                
            # Extract analytics dashboard
            if 'analytics_dashboard' in results:
                dashboard = results['analytics_dashboard']
                
                if 'executive_summary' in dashboard:
                    exec_summary = dashboard['executive_summary']
                    summary['overall_status'] = exec_summary.get('overall_status', 'unknown')
                    summary['critical_alerts'] = len(exec_summary.get('critical_issues', []))
                    
                if 'faction_balance_metrics' in dashboard:
                    balance_metrics = dashboard['faction_balance_metrics']
                    summary['factions_analyzed'] = len(balance_metrics)
                    
        except Exception as e:
            print(f"⚠️  Warning: Error extracting optimization summary: {e}")
            summary['extraction_error'] = str(e)
            
        return summary
        
    def _generate_comprehensive_report(self):
        """Generate comprehensive business intelligence report"""
        
        print("Generating comprehensive business intelligence report...")
        
        # Compile executive summary
        self.executive_summary = {
            'suite_execution_time': datetime.now().isoformat(),
            'total_components_run': len([r for r in self.component_results.values() if r]),
            'statistical_analysis': self.component_results.get('statistical_analysis'),
            'balance_optimization': self.component_results.get('balance_optimization'),
            'overall_assessment': self._calculate_overall_assessment(),
            'key_recommendations': self._generate_key_recommendations(),
            'next_steps': self._generate_next_steps()
        }
        
        # Print executive summary
        self._print_executive_summary()
        
        # Save detailed report
        self._save_detailed_report()
        
    def _calculate_overall_assessment(self):
        """Calculate overall system assessment"""
        
        assessment = {
            'status': 'UNKNOWN',
            'confidence': 0.0,
            'key_findings': []
        }
        
        try:
            # Analyze statistical results
            stat_results = self.component_results.get('statistical_analysis')
            opt_results = self.component_results.get('balance_optimization')
            
            balance_scores = []
            
            if stat_results:
                if 'overall_balance_score' in stat_results:
                    balance_scores.append(stat_results['overall_balance_score'])
                    assessment['key_findings'].append(
                        f"Statistical analysis balance: {stat_results['overall_balance_score']:.1%}"
                    )
                    
            if opt_results:
                if 'optimization_success' in opt_results and opt_results['optimization_success']:
                    assessment['key_findings'].append("Resource bonus optimization successful")
                    
                if 'overall_status' in opt_results:
                    status = opt_results['overall_status']
                    if status in ['healthy', 'good']:
                        balance_scores.append(0.8)
                    elif status == 'warning':
                        balance_scores.append(0.7)
                    elif status == 'critical':
                        balance_scores.append(0.5)
                        
            # Overall assessment
            if balance_scores:
                avg_balance = sum(balance_scores) / len(balance_scores)
                assessment['confidence'] = 0.9
                
                if avg_balance >= 0.8:
                    assessment['status'] = 'EXCELLENT'
                elif avg_balance >= 0.7:
                    assessment['status'] = 'GOOD'
                elif avg_balance >= 0.6:
                    assessment['status'] = 'ACCEPTABLE'
                else:
                    assessment['status'] = 'NEEDS_ATTENTION'
            else:
                assessment['status'] = 'INSUFFICIENT_DATA'
                assessment['confidence'] = 0.3
                
        except Exception as e:
            print(f"⚠️  Warning: Error in overall assessment: {e}")
            assessment['status'] = 'ERROR'
            assessment['error'] = str(e)
            
        return assessment
        
    def _generate_key_recommendations(self):
        """Generate key business recommendations"""
        
        recommendations = []
        
        try:
            assessment = self.executive_summary.get('overall_assessment', {})
            status = assessment.get('status', 'UNKNOWN')
            
            if status == 'EXCELLENT':
                recommendations.extend([
                    "Continue current territorial balance approach",
                    "Implement proactive monitoring for early issue detection", 
                    "Consider minor optimizations based on player feedback"
                ])
            elif status == 'GOOD':
                recommendations.extend([
                    "Maintain current balance parameters with regular monitoring",
                    "Schedule periodic balance reviews",
                    "Prepare contingency adjustments for emerging issues"
                ])
            elif status == 'ACCEPTABLE':
                recommendations.extend([
                    "Implement moderate resource bonus adjustments",
                    "Increase faction performance monitoring frequency",
                    "Execute A/B testing for proposed balance changes"
                ])
            elif status == 'NEEDS_ATTENTION':
                recommendations.extend([
                    "URGENT: Deploy optimized resource bonuses immediately", 
                    "Launch targeted faction engagement initiatives",
                    "Implement emergency balance intervention protocols"
                ])
            else:
                recommendations.extend([
                    "Collect more comprehensive territorial data",
                    "Re-run analytics with updated parameters",
                    "Consult game design team for manual balance review"
                ])
                
            # Add component-specific recommendations
            opt_results = self.component_results.get('balance_optimization')
            if opt_results and opt_results.get('optimization_success'):
                recommendations.append("Deploy the optimized resource bonus configuration")
                
        except Exception as e:
            print(f"⚠️  Warning: Error generating recommendations: {e}")
            recommendations.append("Review analytics suite execution for errors")
            
        return recommendations
        
    def _generate_next_steps(self):
        """Generate next steps for implementation"""
        
        next_steps = []
        
        try:
            assessment = self.executive_summary.get('overall_assessment', {})
            status = assessment.get('status', 'UNKNOWN')
            
            # Common next steps
            next_steps.extend([
                "Review comprehensive analytics report with development team",
                "Update territorial resource configuration based on optimization results",
                "Schedule follow-up analysis in 1-2 weeks to validate changes"
            ])
            
            # Status-specific next steps
            if status in ['NEEDS_ATTENTION', 'CRITICAL']:
                next_steps.insert(0, "IMMEDIATE: Implement emergency balance adjustments")
                next_steps.insert(1, "Deploy real-time monitoring dashboard for ongoing oversight")
                
            # Implementation-specific steps
            opt_results = self.component_results.get('balance_optimization') 
            if opt_results and opt_results.get('optimization_success'):
                next_steps.append("Implement A/B testing framework for validated bonus adjustments")
                
        except Exception as e:
            print(f"⚠️  Warning: Error generating next steps: {e}")
            next_steps.append("Debug analytics suite execution issues")
            
        return next_steps
        
    def _print_executive_summary(self):
        """Print executive summary to console"""
        
        print("\n" + "="*80)
        print("EXECUTIVE SUMMARY - TERRITORIAL ANALYTICS SUITE")
        print("="*80)
        
        # Overall assessment
        assessment = self.executive_summary.get('overall_assessment', {})
        print(f"\nOVERALL ASSESSMENT: {assessment.get('status', 'UNKNOWN')}")
        print(f"Confidence Level: {assessment.get('confidence', 0.0):.1%}")
        
        # Key findings
        print(f"\nKEY FINDINGS:")
        for finding in assessment.get('key_findings', []):
            print(f"  • {finding}")
            
        # Component results
        print(f"\nCOMPONENT RESULTS:")
        for component, results in self.component_results.items():
            if results:
                status_indicator = "✅" if results.get('status') == 'completed' else "⚠️"
                print(f"  {status_indicator} {component.replace('_', ' ').title()}: Completed")
            else:
                print(f"  ❌ {component.replace('_', ' ').title()}: Failed")
                
        # Recommendations
        print(f"\nKEY RECOMMENDATIONS:")
        for i, rec in enumerate(self.executive_summary.get('key_recommendations', [])[:5], 1):
            print(f"  {i}. {rec}")
            
        # Next steps
        print(f"\nNEXT STEPS:")
        for i, step in enumerate(self.executive_summary.get('next_steps', [])[:5], 1):
            print(f"  {i}. {step}")
            
        print("\n" + "="*80)
        
    def _save_detailed_report(self):
        """Save detailed report to JSON file"""
        
        try:
            report_filename = f"territorial_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path = self.script_directory / report_filename
            
            detailed_report = {
                'metadata': {
                    'suite_version': '1.0',
                    'execution_time': self.suite_start_time.isoformat(),
                    'completion_time': datetime.now().isoformat(),
                    'script_directory': str(self.script_directory)
                },
                'executive_summary': self.executive_summary,
                'component_results': self.component_results,
                'component_details': {
                    'statistical_analysis': 'Comprehensive statistical modeling of territorial resource bonuses',
                    'balance_optimization': 'Advanced faction balance optimization with A/B testing framework',
                    'realtime_dashboard': 'Real-time analytics dashboard with anomaly detection'
                }
            }
            
            with open(report_path, 'w') as f:
                json.dump(detailed_report, f, indent=2, default=str)
                
            print(f"\n💾 Detailed report saved: {report_path}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not save detailed report: {e}")
            
    def _print_final_summary(self):
        """Print final summary of suite execution"""
        
        end_time = datetime.now()
        duration = end_time - self.suite_start_time
        
        print("\n" + "="*80)
        print("TERRITORIAL ANALYTICS SUITE - EXECUTION COMPLETE")
        print("="*80)
        
        print(f"\nExecution Summary:")
        print(f"  Start Time: {self.suite_start_time}")
        print(f"  End Time: {end_time}")
        print(f"  Total Duration: {duration}")
        
        successful_components = len([r for r in self.component_results.values() if r])
        print(f"  Components Run: {successful_components}/{len(self.components)}")
        
        assessment = self.executive_summary.get('overall_assessment', {})
        print(f"  Overall Status: {assessment.get('status', 'UNKNOWN')}")
        
        print(f"\nFiles Created:")
        print(f"  • territorial_resource_statistical_analysis.py - Statistical modeling system")
        print(f"  • advanced_faction_balance_optimizer.py - Balance optimization framework")
        print(f"  • realtime_territorial_analytics_dashboard.py - Real-time monitoring system")
        print(f"  • Detailed JSON report (if saved successfully)")
        
        print(f"\nNext Steps:")
        print(f"  1. Review executive summary and recommendations above")
        print(f"  2. Implement suggested resource bonus adjustments")
        print(f"  3. Deploy real-time monitoring for ongoing oversight")
        print(f"  4. Schedule follow-up analysis to validate changes")
        
        print("\n✅ Territorial Analytics Suite execution complete!")
        print("="*80)


def main():
    """Main execution function"""
    
    print("Terminal Grounds - Territorial Analytics Suite Runner")
    print("Comprehensive statistical modeling and balance optimization system")
    print()
    
    # Initialize and run suite
    suite = TerritorialAnalyticsSuite()
    success = suite.run_complete_analytics_suite()
    
    if success:
        print("\n🎉 Analytics suite completed successfully!")
        return 0
    else:
        print("\n❌ Analytics suite execution failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())