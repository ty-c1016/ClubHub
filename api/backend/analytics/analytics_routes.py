from flask import Blueprint, jsonify, request
from backend.db_connection import db
from pymysql import Error
from flask import current_app
from pymysql.cursors import DictCursor
from datetime import datetime, timedelta

analytics_routes = Blueprint("analytics_routes", __name__)

@analytics_routes.route("/analytics/debug/tables", methods=["GET"])
def debug_tables():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        # Check if tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        # Check counts for key tables
        counts = {}
        
        cursor.execute("SELECT COUNT(*) as count FROM Events")
        counts['Events'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Searches")
        counts['Searches'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Search_Result")
        counts['Search_Result'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Students")
        counts['Students'] = cursor.fetchone()['count']
        
        return jsonify({
            "tables": tables,
            "counts": counts
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()

@analytics_routes.route("/analytics/list-routes", methods=["GET"])
def list_routes():
    """List all registered routes"""
    from flask import current_app
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "path": str(rule)
        })
    return jsonify(routes), 200


# GET /analytics/engagement/current-metrics
@analytics_routes.route("/analytics/engagement/current-metrics", methods=["GET"])
def get_current_period_metrics():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
            SELECT
                COUNT(DISTINCT e.eventID) AS total_events,
                (
                    SELECT COUNT(DISTINCT invitation_id)
                    FROM event_invitations
                    WHERE invitation_status = 'accepted'
                      AND sent_datetime >= %s
                ) AS total_rsvps,
                COUNT(DISTINCT sea.attendanceID) AS total_checkins,
                COUNT(DISTINCT sea.studentID) AS active_users
            FROM Events e
            LEFT JOIN Students_Event_Attendees sea 
                ON e.eventID = sea.eventID 
                AND sea.timestamp >= %s
            WHERE e.startDateTime >= %s
        """
        
        cursor.execute(query, (start_date_str, start_date_str, start_date_str))
        result = cursor.fetchone()
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Error fetching current metrics: {e}")
        return jsonify({"error": "Error fetching current metrics"}), 500
    finally:
        if cursor:
            cursor.close()


# GET /analytics/engagement/previous-metrics
@analytics_routes.route("/analytics/engagement/previous-metrics", methods=["GET"])
def get_previous_period_metrics():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        # 30-60 days ago
        end_date = datetime.now() - timedelta(days=30)
        start_date = datetime.now() - timedelta(days=60)

        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
            SELECT
                COUNT(DISTINCT e.eventID) AS total_events,
                (
                    SELECT COUNT(DISTINCT invitation_id)
                    FROM event_invitations
                    WHERE invitation_status = 'accepted'
                      AND sent_datetime >= %s
                      AND sent_datetime < %s
                ) AS total_rsvps,
                COUNT(DISTINCT sea.attendanceID) AS total_checkins,
                COUNT(DISTINCT sea.studentID) AS active_users
            FROM Events e
            LEFT JOIN Students_Event_Attendees sea 
                ON e.eventID = sea.eventID 
                AND sea.timestamp >= %s
                AND sea.timestamp < %s
            WHERE e.startDateTime >= %s
              AND e.startDateTime < %s
        """
        
        cursor.execute(query, (start_date_str, end_date_str, start_date_str, end_date_str, start_date_str, end_date_str))
        result = cursor.fetchone()
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Error fetching previous metrics: {e}")
        return jsonify({"error": "Error fetching previous metrics"}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/engagement/events-by-month
@analytics_routes.route("/analytics/engagement/events-by-month", methods=["GET"])
def get_events_by_month():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        # Last 6 months
        start_date = datetime.now() - timedelta(days=180)
        start_date_str = start_date.strftime('%Y-%m-%d')
        
        query = """
            SELECT
                DATE_FORMAT(startDateTime, '%%Y-%%m') AS month,
                DATE_FORMAT(startDateTime, '%%M %%Y') AS month_name,
                COUNT(DISTINCT eventID) AS event_count
            FROM Events
            WHERE DATE(startDateTime) >= %s
            GROUP BY 
                DATE_FORMAT(startDateTime, '%%Y-%%m'),
                DATE_FORMAT(startDateTime, '%%M %%Y')
            ORDER BY month ASC;
        """
        
        cursor.execute(query, (start_date_str,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"Error fetching events by month: {e}")
        return jsonify({"error": "Error fetching events by month"}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/engagement/top-clubs
@analytics_routes.route("/analytics/engagement/top-clubs", methods=["GET"])
def get_top_clubs_by_engagement():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = datetime.now() - timedelta(days=30)
        
        query = """
            SELECT
                c.clubID,
                c.name AS club_name,
                COUNT(DISTINCT sea.attendanceID) AS total_checkins,
                COUNT(DISTINCT e.eventID) AS events_hosted,
                COUNT(DISTINCT sea.studentID) AS unique_attendees
            FROM Clubs c
            JOIN Events e ON c.clubID = e.clubID
            LEFT JOIN Students_Event_Attendees sea 
                ON e.eventID = sea.eventID
                AND sea.timestamp >= %s
            WHERE e.startDateTime >= %s
            GROUP BY c.clubID, c.name
            HAVING events_hosted > 0
            ORDER BY total_checkins DESC
            LIMIT 10
        """
        
        cursor.execute(query, (start_date, start_date))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"Error fetching top clubs: {e}")
        return jsonify({"error": "Error fetching top clubs"}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/engagement/engagement-rate
@analytics_routes.route("/analytics/engagement/engagement-rate", methods=["GET"])
def get_engagement_rate():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = datetime.now() - timedelta(days=30)
        
        query = """
            SELECT
                COUNT(DISTINCT sea.studentID) AS active_students,
                (SELECT COUNT(*) FROM Students) AS total_students,
                ROUND(
                    (COUNT(DISTINCT sea.studentID) / (SELECT COUNT(*) FROM Students)) * 100,
                    2
                ) AS engagement_rate
            FROM Students_Event_Attendees sea
            WHERE sea.timestamp >= %s
        """
        
        cursor.execute(query, (start_date,))
        result = cursor.fetchone()
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Error calculating engagement rate: {e}")
        return jsonify({"error": "Error calculating engagement rate"}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/search/summary
@analytics_routes.route("/analytics/search/summary", methods=["GET"])
def get_search_summary():
    """Get search summary metrics (last 90 days)"""
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT
                COUNT(*) as total_searches,
                COUNT(DISTINCT searchQuery) as unique_queries,
                (SELECT COUNT(DISTINCT s.searchID) 
                 FROM Searches s
                 LEFT JOIN Searches_Search_Results ssr ON s.searchID = ssr.searchID
                 WHERE DATE(s.timestamp) >= %s 
                   AND ssr.resultID IS NULL) as no_result_searches
            FROM Searches
            WHERE DATE(timestamp) >= %s
        """
        
        cursor.execute(query, (start_date, start_date))
        result = cursor.fetchone()
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching search summary: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/search/top-keywords
@analytics_routes.route("/analytics/search/top-keywords", methods=["GET"])
def get_top_keywords():
    """Get most searched keywords with CTR data"""
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT
                s.searchQuery as query,
                COUNT(DISTINCT s.searchID) as search_count,
                COUNT(DISTINCT ssr.resultID) as total_results,
                ROUND(COUNT(DISTINCT ssr.resultID) * 1.0 / COUNT(DISTINCT s.searchID), 1) as avg_results,
                SUM(sr.clicks) as clicks,
                ROUND(SUM(sr.clicks) * 100.0 / COUNT(DISTINCT s.searchID), 1) as ctr
            FROM Searches s
            LEFT JOIN Searches_Search_Results ssr ON s.searchID = ssr.searchID
            LEFT JOIN Search_Result sr ON ssr.resultID = sr.resultID
            WHERE DATE(s.timestamp) >= %s
            GROUP BY s.searchQuery
            HAVING search_count > 0
            ORDER BY search_count DESC
            LIMIT 20
        """
        
        cursor.execute(query, (start_date,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching top keywords: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/search/no-results
@analytics_routes.route("/analytics/search/no-results", methods=["GET"])
def get_no_result_searches():
    """Get searches that returned no results"""
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT
                s.searchQuery as query,
                COUNT(*) as search_count
            FROM Searches s
            LEFT JOIN Searches_Search_Results ssr ON s.searchID = ssr.searchID
            WHERE DATE(s.timestamp) >= %s
              AND ssr.resultID IS NULL
            GROUP BY s.searchQuery
            ORDER BY search_count DESC
            LIMIT 20
        """
        
        cursor.execute(query, (start_date,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching no-result searches: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/demographics
@analytics_routes.route("/analytics/demographics", methods=["GET"])
def get_demographic_engagement():
    """
    Return engagement analysis by student demographics.

    Conceptually matches Part 3 SQL:

    FROM Students s
      LEFT JOIN RSVPs r ON s.student_id = r.student_id
      LEFT JOIN Attendance a ON s.student_id = a.student_id
           AND r.event_id = a.event_id

    with fields like s.student_year, s.major, r.created_datetime, etc.
    """
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        query = """
            SELECT 
                s.student_year,
                s.major,
                COUNT(DISTINCT r.student_id) AS students_with_rsvps,
                COUNT(DISTINCT r.event_id) AS unique_events_rsvped,
                COUNT(r.rsvp_id) AS total_rsvps,
                COUNT(DISTINCT a.event_id) AS events_attended,
                ROUND(
                    COUNT(DISTINCT a.event_id) * 100.0 /
                    NULLIF(COUNT(DISTINCT r.event_id), 0),
                    2
                ) AS attendance_rate
            FROM Students s
            LEFT JOIN RSVPs r 
                ON s.student_id = r.student_id
            LEFT JOIN Attendance a 
                ON s.student_id = a.student_id
               AND r.event_id = a.event_id
            WHERE r.created_datetime >= NOW() - INTERVAL 90 DAY
            GROUP BY s.student_year, s.major
            ORDER BY total_rsvps DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"Error fetching demographic engagement: {e}")
        return jsonify({"error": "Error fetching demographic engagement"}), 500
    finally:
        if cursor:
            cursor.close()



# GET /analytics/reports
@analytics_routes.route("/analytics/reports", methods=["GET"])
def get_engagement_reports():
    """
    Return generated engagement reports.

    Expects engagement_reports table with columns:
      - report_id
      - report_period_start
      - report_period_end
      - total_active_users
      - total_events_created
      - total_rsvps
      - total_attendance
      - total_searches
      - generated_datetime
    """
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        query = """
            SELECT 
                report_id,
                report_period_start,
                report_period_end,
                total_active_users,
                total_events_created,
                total_rsvps,
                total_attendance,
                total_searches,
                generated_datetime
            FROM Engagement_Reports
            ORDER BY generated_datetime DESC
            LIMIT 50;
        """
        cursor.execute(query)
        reports = cursor.fetchall()
        return jsonify(reports), 200
    except Error as e:
        current_app.logger.error(f"Error fetching engagement reports: {e}")
        return jsonify({"error": "Error fetching engagement reports"}), 500
    finally:
        if cursor:
            cursor.close()



# POST /analytics/reports
@analytics_routes.route("/analytics/reports", methods=["POST"])
def generate_weekly_engagement_report():
    """
    Generate and save a weekly engagement report.

    This is a MySQL-ish adaptation of your Part 3 query.

    It summarizes the last 7 days of activity in audit_logs
    into a single row in engagement_reports.
    """
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)

        insert_query = """
            INSERT INTO Engagement_Reports 
                (report_period_start,
                 report_period_end,
                 total_active_users,
                 total_events_created,
                 total_rsvps,
                 total_attendance,
                 total_searches,
                 generated_datetime)
            SELECT
                DATE_SUB(CURDATE(), INTERVAL 7 DAY) AS report_period_start,
                CURDATE() AS report_period_end,
                COUNT(DISTINCT CASE 
                    WHEN al.action_type IN ('login', 'event_view', 'search')
                    THEN al.user_id
                END) AS total_active_users,
                COUNT(DISTINCT CASE 
                    WHEN al.action_type = 'event_created'
                    THEN al.entity_id
                END) AS total_events_created,
                COUNT(DISTINCT CASE 
                    WHEN al.action_type = 'rsvp_created'
                    THEN al.log_id
                END) AS total_rsvps,
                COUNT(DISTINCT CASE 
                    WHEN al.action_type = 'check_in'
                    THEN al.log_id
                END) AS total_attendance,
                COUNT(DISTINCT CASE 
                    WHEN al.action_type = 'search'
                    THEN al.log_id
                END) AS total_searches,
                NOW() AS generated_datetime
            FROM Audit_Logs al
            WHERE al.timestamp >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
              AND al.timestamp < CURDATE() + INTERVAL 1 DAY;
        """

        cursor.execute(insert_query)
        db.commit()

        return jsonify({"message": "Weekly engagement report generated"}), 201
    except Error as e:
        current_app.logger.error(f"Error generating engagement report: {e}")
        return jsonify({"error": "Error generating engagement report"}), 500
    finally:
        if cursor:
            cursor.close()