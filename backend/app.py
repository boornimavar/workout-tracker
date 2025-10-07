from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import config

app = Flask(__name__)
CORS(app)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
def get_sheet():
    try:
        creds = Credentials.from_service_account_file(
            config.CREDENTIALS_FILE, 
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(config.SPREADSHEET_ID)
        
        try:
            worksheet = spreadsheet.worksheet(config.WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=config.WORKSHEET_NAME, 
                rows=1000, 
                cols=10
            )
            worksheet.append_row([
                'ID', 'Timestamp', 'Workout Type', 
                'Duration (min)', 'Intensity', 'Notes'
            ])
        
        return worksheet
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Server is running"}), 200

@app.route('/api/workouts', methods=['POST'])
def add_workout():
    try:
        data = request.json
        
        workout_id = datetime.now().strftime('%Y%m%d%H%M%S')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        workout_type = data.get('type', '')
        duration = data.get('duration', 0)
        intensity = data.get('intensity', '')
        notes = data.get('notes', '')
        sheet = get_sheet()
        if not sheet:
            return jsonify({"error": "Could not connect to Google Sheets"}), 500
        
        row = [workout_id, timestamp, workout_type, duration, intensity, notes]
        sheet.append_row(row)
        
        return jsonify({
            "success": True,
            "message": "Workout logged successfully",
            "workout": {
                "id": workout_id,
                "timestamp": timestamp,
                "type": workout_type,
                "duration": duration,
                "intensity": intensity,
                "notes": notes
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    try:
        sheet = get_sheet()
        if not sheet:
            return jsonify({"error": "Could not connect to Google Sheets"}), 500
        
        all_records = sheet.get_all_records()
        
        workouts = []
        for record in reversed(all_records):
            workouts.append({
                "id": record.get('ID', ''),
                "timestamp": record.get('Timestamp', ''),
                "type": record.get('Workout Type', ''),
                "duration": record.get('Duration (min)', 0),
                "intensity": record.get('Intensity', ''),
                "notes": record.get('Notes', '')
            })
        
        return jsonify({
            "success": True,
            "count": len(workouts),
            "workouts": workouts
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/workouts/<workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    try:
        sheet = get_sheet()
        if not sheet:
            return jsonify({"error": "Could not connect to Google Sheets"}), 500
        
        cell = sheet.find(workout_id)
        if cell:
            sheet.delete_rows(cell.row)
            return jsonify({
                "success": True,
                "message": "Workout deleted successfully"
            }), 200
        else:
            return jsonify({"error": "Workout not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Workout Tracker API")
    print(f"Connected to Google Sheet ID: {config.SPREADSHEET_ID}")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)