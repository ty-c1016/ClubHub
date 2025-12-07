import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Collaborations - ClubHub",
    page_icon="🤝",
    layout="wide")

CLUB_ID = 101  # Latin American Student Union

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🎭 Sofia's Pages")
st.sidebar.markdown("**Current:** Collaborations")
st.sidebar.page_link("pages/6_Sofia_My_Events.py", label="My Events")
st.sidebar.page_link("pages/7_Sofia_Create_Event.py", label="Create Event")
st.sidebar.page_link("pages/8_Sofia_RSVPs.py", label="RSVPs")
st.sidebar.page_link("pages/9_Sofia_Analytics.py", label="Analytics")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("🤝 Collaboration Opportunities")
st.markdown("Discover clubs that host similar events for cross-promotion and partnerships")
st.divider()

# Fetch similar clubs
@st.cache_data(ttl=300)
def fetch_similar_clubs(club_id):
    try:
        response = requests.get(f"{API_BASE_URL}/clubs/{club_id}/similar", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return []

# Fetch own club info
@st.cache_data(ttl=300)
def fetch_club_info(club_id):
    try:
        response = requests.get(f"{API_BASE_URL}/clubs/{club_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

# Get data
similar_clubs = fetch_similar_clubs(CLUB_ID)
own_club = fetch_club_info(CLUB_ID)

if own_club:
    st.info(f"🎭 Finding collaboration opportunities for **{own_club.get('club_name', 'Your Club')}** in the **{own_club.get('category', 'N/A')}** category")
    st.divider()

if not similar_clubs:
    st.warning("No similar clubs found for collaboration opportunities")
    st.markdown("### 💡 Tips for Finding Collaborators")
    st.markdown("""
    - Host more events to increase your visibility
    - Update your club category to match your activities
    - Reach out directly to clubs with similar missions
    """)
else:
    # Summary metrics
    st.markdown("### 📊 Collaboration Potential")
    col1, col2, col3, col4 = st.columns(4)
    
    total_clubs = len(similar_clubs)
    df = pd.DataFrame(similar_clubs)
    
    avg_events = df['total_events'].mean() if 'total_events' in df.columns else 0
    avg_attendance = df['avg_attendance'].mean() if 'avg_attendance' in df.columns else 0
    total_reach = df['avg_attendance'].sum() if 'avg_attendance' in df.columns else 0
    
    with col1:
        st.metric("Similar Clubs", total_clubs)
    
    with col2:
        st.metric("Avg Events per Club", f"{avg_events:.1f}")
    
    with col3:
        st.metric("Avg Attendance", f"{avg_attendance:.0f}")
    
    with col4:
        st.metric("Total Potential Reach", f"{total_reach:.0f}")
    
    st.divider()
    
    # Visualization
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        st.markdown("### 📈 Club Activity Levels")
        if 'club_name' in df.columns and 'total_events' in df.columns:
            fig_events = px.bar(
                df.sort_values('total_events', ascending=False).head(10),
                x='club_name',
                y='total_events',
                title='Top 10 Most Active Clubs',
                color='total_events',
                color_continuous_scale='Teal',
                labels={'club_name': 'Club', 'total_events': 'Total Events'}
            )
            fig_events.update_xaxes(tickangle=45)
            st.plotly_chart(fig_events, use_container_width=True)
        else:
            st.info("No activity data available")
    
    with col_viz2:
        st.markdown("### 👥 Average Attendance by Club")
        if 'club_name' in df.columns and 'avg_attendance' in df.columns:
            fig_attendance = px.bar(
                df.sort_values('avg_attendance', ascending=False).head(10),
                x='club_name',
                y='avg_attendance',
                title='Top 10 Highest Attended Clubs',
                color='avg_attendance',
                color_continuous_scale='Blues',
                labels={'club_name': 'Club', 'avg_attendance': 'Avg Attendance'}
            )
            fig_attendance.update_xaxes(tickangle=45)
            st.plotly_chart(fig_attendance, use_container_width=True)
        else:
            st.info("No attendance data available")
    
    st.divider()
    
    # Category breakdown
    if 'category' in df.columns:
        st.markdown("### 📂 Clubs by Category")
        category_counts = df['category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        
        fig_pie = px.pie(
            category_counts,
            values='Count',
            names='Category',
            title='Distribution of Similar Clubs'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    
    # Detailed club list
    st.markdown("### 🎯 Recommended Clubs for Collaboration")
    
    # Filter and sort options
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        if 'category' in df.columns:
            categories = ['All Categories'] + sorted(df['category'].unique().tolist())
            selected_category = st.selectbox("Filter by Category", categories)
        else:
            selected_category = 'All Categories'
    
    with col_filter2:
        sort_options = {
            'Most Events': 'total_events',
            'Highest Attendance': 'avg_attendance',
            'Alphabetical': 'club_name'
        }
        selected_sort = st.selectbox("Sort By", list(sort_options.keys()))
    
    # Apply filters
    filtered_df = df.copy()
    if selected_category != 'All Categories':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    # Sort
    sort_col = sort_options[selected_sort]
    if sort_col in filtered_df.columns:
        ascending = True if selected_sort == 'Alphabetical' else False
        filtered_df = filtered_df.sort_values(sort_col, ascending=ascending)
    
    st.markdown(f"**Showing {len(filtered_df)} clubs**")
    
    # Display clubs
    for idx, club in filtered_df.iterrows():
        with st.container(border=True):
            col_club1, col_club2 = st.columns([2, 1])
            
            with col_club1:
                st.markdown(f"### {club.get('club_name', 'Unknown Club')}")
                
                category = club.get('category', 'N/A')
                st.markdown(f"**📂 Category:** {category}")
                
                contact = club.get('contact_email', 'N/A')
                if contact != 'N/A':
                    st.markdown(f"📧 {contact}")
                
                # Collaboration score (based on activity and attendance)
                total_events = club.get('total_events', 0)
                avg_att = club.get('avg_attendance', 0)
                
                if total_events >= 10 and avg_att >= 50:
                    st.success("🌟 Highly Recommended - Very Active")
                elif total_events >= 5 and avg_att >= 30:
                    st.info("⭐ Recommended - Moderately Active")
                else:
                    st.markdown("💡 Potential Partner")
            
            with col_club2:
                st.markdown("#### 📊 Activity Stats")
                
                total_events = int(club.get('total_events', 0))
                avg_att = club.get('avg_attendance', 0)
                
                st.metric("Total Events", total_events)
                st.metric("Avg Attendance", f"{avg_att:.0f}")
                
                if st.button("📧 Contact", key=f"contact_{club.get('club_id')}", use_container_width=True):
                    email = club.get('contact_email', '')
                    if email:
                        st.success(f"Contact them at: {email}")
                    else:
                        st.info("No contact email available")
    
    st.divider()
    
    # Collaboration tips
    with st.expander("💡 Tips for Successful Collaborations"):
        st.markdown("""
        ### Building Strong Partnerships
        
        **Why Collaborate?**
        - Reach new audiences and expand your network
        - Share resources and reduce costs
        - Create more impactful and diverse events
        - Build lasting relationships with other organizations
        
        **How to Reach Out:**
        1. Identify shared goals and complementary strengths
        2. Propose specific collaboration ideas (co-hosted events, cross-promotion)
        3. Be clear about expectations and responsibilities
        4. Start small and build trust over time
        
        **Best Practices:**
        - Schedule regular check-ins with partner clubs
        - Clearly define roles and resource sharing
        - Promote each other's events on your platforms
        - Evaluate collaboration success and iterate
        """)

# Export and refresh
st.divider()
col_action1, col_action2, col_action3 = st.columns([1, 1, 2])

with col_action1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col_action2:
    if similar_clubs:
        csv = pd.DataFrame(similar_clubs).to_csv(index=False)
        st.download_button(
            label="📥 Download List",
            data=csv,
            file_name=f"collaboration_opportunities.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.divider()
st.markdown("*Similar clubs are identified based on shared categories and event types. Clubs with 5+ events are prioritized.*")