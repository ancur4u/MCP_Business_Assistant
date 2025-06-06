import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import time
import random
from typing import Dict, List, Any

# Page configuration
st.set_page_config(
    page_title="MCP Business Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .tool-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .connected {
        border-left: 4px solid #4CAF50;
        background: #f8fff8;
    }
    .disconnected {
        border-left: 4px solid #f44336;
        background: #fff8f8;
    }
    .query-result {
        background: #e8f5e8;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
        font-family: monospace;
        white-space: pre-wrap;
    }
    .processing {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    .metric-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        min-width: 120px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'connected_tools' not in st.session_state:
    st.session_state.connected_tools = set()
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

class MCPToolManager:
    """Manages MCP tool connections and data retrieval"""
    
    def __init__(self):
        self.tools = {
            'asana': {
                'name': 'Asana',
                'description': 'Project Management',
                'icon': '📋',
                'category': 'productivity'
            },
            'google_analytics': {
                'name': 'Google Analytics',
                'description': 'Web Analytics',
                'icon': '📈',
                'category': 'analytics'
            },
            'quickbooks': {
                'name': 'QuickBooks',
                'description': 'Accounting & Finance',
                'icon': '💰',
                'category': 'finance'
            },
            'zendesk': {
                'name': 'Zendesk',
                'description': 'Customer Support',
                'icon': '🎫',
                'category': 'support'
            },
            'google_calendar': {
                'name': 'Google Calendar',
                'description': 'Team Scheduling',
                'icon': '📅',
                'category': 'productivity'
            },
            'hootsuite': {
                'name': 'Hootsuite',
                'description': 'Social Media Management',
                'icon': '📱',
                'category': 'marketing'
            },
            'hubspot': {
                'name': 'HubSpot CRM',
                'description': 'Customer Relationship Management',
                'icon': '🏢',
                'category': 'sales'
            },
            'slack': {
                'name': 'Slack',
                'description': 'Team Communication',
                'icon': '💬',
                'category': 'communication'
            }
        }
        
        self.mock_data = self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize comprehensive mock data"""
        return {
            'asana': {
                'projects': [
                    {'name': 'Johnson Marketing Campaign', 'status': 'On Track', 'progress': 75, 'due_date': '2025-06-15'},
                    {'name': 'Tech Startup Rebrand', 'status': 'Behind Schedule', 'progress': 45, 'due_date': '2025-06-10'},
                    {'name': 'E-commerce Platform Launch', 'status': 'Ahead of Schedule', 'progress': 92, 'due_date': '2025-06-20'}
                ],
                'team_workload': {
                    'Alex': {'utilization': 85, 'availability': 'Busy'},
                    'Sarah': {'utilization': 92, 'availability': 'Overloaded'},
                    'Mike': {'utilization': 78, 'availability': 'Available'},
                    'Lisa': {'utilization': 88, 'availability': 'Busy'}
                }
            },
            'google_analytics': {
                'page_views': 45600,
                'conversion_rate': 3.2,
                'bounce_rate': 32.5,
                'top_pages': [
                    {'page': '/landing-page', 'views': 8900},
                    {'page': '/services', 'views': 6700},
                    {'page': '/about', 'views': 4200}
                ]
            },
            'quickbooks': {
                'monthly_revenue': 78450,
                'outstanding_invoices': 23400,
                'profit_margin': 42.4,
                'expenses': 45200
            },
            'zendesk': {
                'tickets': [
                    {'client': 'TechCorp', 'subject': 'Login Issues', 'priority': 'High', 'status': 'Open'},
                    {'client': 'RetailPlus', 'subject': 'Analytics Question', 'priority': 'Medium', 'status': 'In Progress'},
                    {'client': 'StartupHub', 'subject': 'Feature Request', 'priority': 'Low', 'status': 'Pending'}
                ],
                'avg_response_time': '2.5 hours',
                'customer_satisfaction': 4.6
            },
            'google_calendar': {
                'meetings_today': 5,
                'availability': {
                    'Alex': 'Busy until 3 PM',
                    'Sarah': 'Available after 11 AM',
                    'Mike': 'Free all day',
                    'Lisa': 'Busy 2-4 PM'
                }
            },
            'hootsuite': {
                'total_followers': 28600,
                'engagement_rate': 4.8,
                'posts_this_week': 12,
                'reach': 45600
            },
            'hubspot': {
                'pipeline_value': 567800,
                'deals_won': 12,
                'conversion_rate': 26.7,
                'new_leads': 23
            },
            'slack': {
                'messages_today': 156,
                'active_users': 8,
                'urgent_mentions': 3
            }
        }
    
    def get_tool_data(self, tool_id: str):
        return self.mock_data.get(tool_id, {})
    
    def is_connected(self, tool_id: str):
        return tool_id in st.session_state.connected_tools

class MCPQueryProcessor:
    """Processes queries across multiple connected tools"""
    
    def __init__(self, tool_manager: MCPToolManager):
        self.tool_manager = tool_manager
    
    def process_query(self, query: str) -> str:
        """Process a query and return comprehensive response"""
        connected_tools = list(st.session_state.connected_tools)
        
        if not connected_tools:
            return "❌ No tools connected. Please connect your business tools to get AI-powered insights."
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['summary', 'overview', 'executive']):
            return self._generate_executive_summary(connected_tools)
        elif any(word in query_lower for word in ['project', 'task']):
            return self._generate_project_report(connected_tools)
        elif any(word in query_lower for word in ['revenue', 'financial', 'money']):
            return self._generate_financial_report(connected_tools)
        elif any(word in query_lower for word in ['team', 'availability']):
            return self._generate_team_report(connected_tools)
        elif any(word in query_lower for word in ['support', 'ticket']):
            return self._generate_support_report(connected_tools)
        else:
            return self._generate_general_insights(connected_tools, query)
    
    def _generate_executive_summary(self, connected_tools):
        summary = f"📊 EXECUTIVE SUMMARY\nGenerated from {len(connected_tools)} connected tools\n\n"
        
        if 'asana' in connected_tools:
            data = self.tool_manager.get_tool_data('asana')
            projects = data['projects']
            avg_progress = sum(p['progress'] for p in projects) / len(projects)
            summary += f"📋 PROJECTS:\n"
            summary += f"• Average progress: {avg_progress:.1f}%\n"
            summary += f"• {sum(1 for p in projects if p['status'] == 'On Track')} on track, "
            summary += f"{sum(1 for p in projects if p['status'] == 'Behind Schedule')} behind\n\n"
        
        if 'quickbooks' in connected_tools:
            data = self.tool_manager.get_tool_data('quickbooks')
            summary += f"💰 FINANCIAL:\n"
            summary += f"• Monthly revenue: ${data['monthly_revenue']:,}\n"
            summary += f"• Outstanding invoices: ${data['outstanding_invoices']:,}\n"
            summary += f"• Profit margin: {data['profit_margin']}%\n\n"
        
        if 'zendesk' in connected_tools:
            data = self.tool_manager.get_tool_data('zendesk')
            high_priority = sum(1 for t in data['tickets'] if t['priority'] == 'High')
            summary += f"🎫 SUPPORT:\n"
            summary += f"• {len(data['tickets'])} active tickets\n"
            summary += f"• {high_priority} high priority issues\n"
            summary += f"• Customer satisfaction: {data['customer_satisfaction']}/5.0\n\n"
        
        if 'google_analytics' in connected_tools:
            data = self.tool_manager.get_tool_data('google_analytics')
            summary += f"📈 WEBSITE:\n"
            summary += f"• Page views: {data['page_views']:,}\n"
            summary += f"• Conversion rate: {data['conversion_rate']}%\n"
            summary += f"• Bounce rate: {data['bounce_rate']}%\n\n"
        
        summary += "🎯 KEY ACTIONS:\n"
        if 'asana' in connected_tools:
            behind_projects = [p for p in self.tool_manager.get_tool_data('asana')['projects'] 
                             if p['status'] == 'Behind Schedule']
            if behind_projects:
                summary += f"• Focus on {len(behind_projects)} behind-schedule projects\n"
        
        if 'quickbooks' in connected_tools:
            outstanding = self.tool_manager.get_tool_data('quickbooks')['outstanding_invoices']
            if outstanding > 20000:
                summary += f"• Follow up on outstanding invoices\n"
        
        return summary
    
    def _generate_project_report(self, connected_tools):
        if 'asana' not in connected_tools:
            return "❌ Project management tool (Asana) not connected."
        
        data = self.tool_manager.get_tool_data('asana')
        projects = data['projects']
        
        report = "📋 PROJECT STATUS REPORT\n\n"
        for project in projects:
            status_emoji = "🟢" if project['status'] == 'On Track' else "🟡" if project['status'] == 'Behind Schedule' else "🔵"
            report += f"{status_emoji} {project['name']}\n"
            report += f"   Progress: {project['progress']}%\n"
            report += f"   Status: {project['status']}\n"
            report += f"   Due: {project['due_date']}\n\n"
        
        return report
    
    def _generate_financial_report(self, connected_tools):
        if 'quickbooks' not in connected_tools:
            return "❌ Accounting tool (QuickBooks) not connected."
        
        data = self.tool_manager.get_tool_data('quickbooks')
        
        report = f"💰 FINANCIAL REPORT\n\n"
        report += f"📈 Revenue: ${data['monthly_revenue']:,}\n"
        report += f"📋 Outstanding: ${data['outstanding_invoices']:,}\n"
        report += f"💸 Expenses: ${data['expenses']:,}\n"
        report += f"📊 Profit Margin: {data['profit_margin']}%\n"
        
        return report
    
    def _generate_team_report(self, connected_tools):
        report = "👥 TEAM REPORT\n\n"
        
        if 'asana' in connected_tools:
            data = self.tool_manager.get_tool_data('asana')
            workload = data['team_workload']
            
            report += "💼 WORKLOAD:\n"
            for member, stats in workload.items():
                status_emoji = "🔴" if stats['availability'] == 'Overloaded' else "🟡" if stats['availability'] == 'Busy' else "🟢"
                report += f"{status_emoji} {member}: {stats['utilization']}% - {stats['availability']}\n"
            report += "\n"
        
        if 'google_calendar' in connected_tools:
            data = self.tool_manager.get_tool_data('google_calendar')
            report += f"📅 MEETINGS TODAY: {data['meetings_today']}\n\n"
            report += "🕐 AVAILABILITY:\n"
            for member, status in data['availability'].items():
                report += f"• {member}: {status}\n"
        
        return report
    
    def _generate_support_report(self, connected_tools):
        if 'zendesk' not in connected_tools:
            return "❌ Support tool (Zendesk) not connected."
        
        data = self.tool_manager.get_tool_data('zendesk')
        tickets = data['tickets']
        
        report = "🎫 SUPPORT REPORT\n\n"
        report += "📋 ACTIVE TICKETS:\n"
        for ticket in tickets:
            priority_emoji = "🔴" if ticket['priority'] == 'High' else "🟡" if ticket['priority'] == 'Medium' else "🟢"
            report += f"{priority_emoji} {ticket['client']}: {ticket['subject']} ({ticket['status']})\n"
        
        report += f"\n📊 METRICS:\n"
        report += f"• Response time: {data['avg_response_time']}\n"
        report += f"• Satisfaction: {data['customer_satisfaction']}/5.0\n"
        
        return report
    
    def _generate_general_insights(self, connected_tools, query):
        insights = f"🤖 AI ANALYSIS\n\n"
        insights += f"Query: {query}\n"
        insights += f"Connected tools: {len(connected_tools)}\n\n"
        insights += "Available commands:\n"
        insights += "• 'executive summary' - comprehensive overview\n"
        insights += "• 'project status' - project details\n"
        insights += "• 'financial report' - revenue and expenses\n"
        insights += "• 'team availability' - workload and schedule\n"
        insights += "• 'support tickets' - customer issues\n"
        
        return insights

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 MCP Business Assistant</h1>
        <p>Connect your business tools and get AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize managers
    tool_manager = MCPToolManager()
    query_processor = MCPQueryProcessor(tool_manager)
    
    # Sidebar - Tool Connections
    with st.sidebar:
        st.header("🔗 MCP Tool Connections")
        
        # Connection status
        connected_count = len(st.session_state.connected_tools)
        st.metric("Connected Tools", connected_count, len(tool_manager.tools) - connected_count)
        
        st.markdown("---")
        
        # Tool connection interface
        for tool_id, tool_info in tool_manager.tools.items():
            is_connected = tool_manager.is_connected(tool_id)
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="tool-card {'connected' if is_connected else 'disconnected'}">
                        <strong>{tool_info['icon']} {tool_info['name']}</strong><br>
                        <small>{tool_info['description']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("Disconnect" if is_connected else "Connect", 
                               key=f"btn_{tool_id}",
                               type="secondary" if is_connected else "primary"):
                        if is_connected:
                            st.session_state.connected_tools.discard(tool_id)
                        else:
                            st.session_state.connected_tools.add(tool_id)
                        st.rerun()
        
        # Security info
        st.markdown("---")
        st.info("🛡️ MCP ensures secure, standardized communication between AI and your business tools")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Ask Your AI Assistant")
        
        # Predefined queries
        st.subheader("Quick Actions")
        quick_actions = [
            "Generate executive summary",
            "Show project status",
            "Financial report",
            "Team availability",
            "Support tickets overview"
        ]
        
        cols = st.columns(len(quick_actions))
        for i, action in enumerate(quick_actions):
            with cols[i]:
                if st.button(action, key=f"quick_{i}", use_container_width=True):
                    with st.spinner("Processing query..."):
                        result = query_processor.process_query(action)
                        st.session_state.query_history.append({
                            'query': action,
                            'result': result,
                            'timestamp': datetime.now()
                        })
        
        # Custom query
        st.subheader("Custom Query")
        user_query = st.text_input("Ask anything about your business:", 
                                 placeholder="e.g., What's our team workload this week?")
        
        if st.button("🚀 Ask AI", type="primary", use_container_width=True):
            if user_query:
                with st.spinner("Processing your query using MCP connections..."):
                    time.sleep(1)  # Simulate processing
                    result = query_processor.process_query(user_query)
                    st.session_state.query_history.append({
                        'query': user_query,
                        'result': result,
                        'timestamp': datetime.now()
                    })
        
        # Query results
        if st.session_state.query_history:
            st.subheader("🤖 AI Response")
            latest_query = st.session_state.query_history[-1]
            
            st.markdown(f"""
            <div class="query-result">
{latest_query['result']}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.header("📊 Dashboard")
        
        # Show data from connected tools
        if st.session_state.connected_tools:
            for tool_id in st.session_state.connected_tools:
                tool_info = tool_manager.tools[tool_id]
                data = tool_manager.get_tool_data(tool_id)
                
                with st.expander(f"{tool_info['icon']} {tool_info['name']}", expanded=False):
                    if tool_id == 'asana' and data:
                        st.metric("Active Projects", len(data['projects']))
                        for project in data['projects']:
                            st.progress(project['progress'] / 100, f"{project['name']}: {project['progress']}%")
                    
                    elif tool_id == 'quickbooks' and data:
                        st.metric("Monthly Revenue", f"${data['monthly_revenue']:,}")
                        st.metric("Outstanding", f"${data['outstanding_invoices']:,}")
                        st.metric("Profit Margin", f"{data['profit_margin']}%")
                    
                    elif tool_id == 'google_analytics' and data:
                        st.metric("Page Views", f"{data['page_views']:,}")
                        st.metric("Conversion Rate", f"{data['conversion_rate']}%")
                        st.metric("Bounce Rate", f"{data['bounce_rate']}%")
                    
                    elif tool_id == 'zendesk' and data:
                        st.metric("Active Tickets", len(data['tickets']))
                        st.metric("Customer Satisfaction", f"{data['customer_satisfaction']}/5.0")
                    
                    elif tool_id == 'hootsuite' and data:
                        st.metric("Total Followers", f"{data['total_followers']:,}")
                        st.metric("Engagement Rate", f"{data['engagement_rate']}%")
        else:
            st.info("Connect tools to see live data dashboard")
        
        # Query history
        if st.session_state.query_history:
            st.subheader("📜 Query History")
            for i, query_item in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history) - i}", expanded=False):
                    st.write(f"**Query:** {query_item['query']}")
                    st.write(f"**Time:** {query_item['timestamp'].strftime('%H:%M:%S')}")
                    st.text_area("Result:", query_item['result'], height=100, key=f"history_{i}")

    # Footer
    st.markdown("---")
    st.markdown("""
    ### 🚀 How This MCP Prototype Works:
    1. **Connect Tools:** Use the sidebar to simulate real business tool integrations
    2. **Ask Questions:** Use natural language to query across multiple systems
    3. **Get Insights:** AI provides unified responses from all connected data sources
    4. **Real-time Updates:** See live data from connected tools in the dashboard
    
    **Real MCP Benefits:** No more switching between 15+ browser tabs, instant cross-platform insights, 
    secure data access, and AI that understands your entire business context.
    """)

if __name__ == "__main__":
    main()