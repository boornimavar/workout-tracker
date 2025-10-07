const API_URL = 'https://workout-tracker-rve4.onrender.com';

const form = document.getElementById('workoutForm');
const workoutList = document.getElementById('workoutList');
const loadBtn = document.getElementById('loadBtn');
const statusDiv = document.getElementById('status');

function showStatus(message, isError = false) {
    statusDiv.textContent = message;
    statusDiv.className = isError ? 'status error' : 'status success';
    statusDiv.style.display = 'block';
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

async function logWorkout(workoutData) {
    try {
        const response = await fetch(`${API_URL}/workouts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(workoutData)
        });

        const data = await response.json();

        if (response.ok) {
            showStatus(`✓ ${workoutData.type} workout logged successfully!`);
            loadWorkouts();
            return true;
        } else {
            showStatus(`⚠ Error: ${data.error}`, true);
            return false;
        }
    } catch (error) {
        showStatus(`⚠ Connection error: ${error.message}`, true);
        return false;
    }
}

async function loadWorkouts() {
    try {
        loadBtn.disabled = true;
        loadBtn.textContent = '[ LOADING... ]';

        const response = await fetch(`${API_URL}/workouts`);
        const data = await response.json();

        if (response.ok) {
            displayWorkouts(data.workouts);
            showStatus(`✓ Loaded ${data.count} workout(s)`);
        } else {
            showStatus(`⚠ Error: ${data.error}`, true);
        }
    } catch (error) {
        showStatus(`⚠ Connection error: ${error.message}`, true);
    } finally {
        loadBtn.disabled = false;
        loadBtn.textContent = '[ LOAD HISTORY ]';
    }
}

async function deleteWorkout(workoutId) {
    if (!confirm('Delete this workout?')) return;

    try {
        const response = await fetch(`${API_URL}/workouts/${workoutId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            showStatus('✓ Workout deleted successfully');
            loadWorkouts();
        } else {
            showStatus(`⚠ Error: ${data.error}`, true);
        }
    } catch (error) {
        showStatus(`⚠ Connection error: ${error.message}`, true);
    }
}

function displayWorkouts(workouts) {
    if (!workouts || workouts.length === 0) {
        workoutList.innerHTML = '<div style="color: #ff00ff; text-align: center; padding: 20px;">[ NO WORKOUTS LOGGED YET ]</div>';
        return;
    }

    workoutList.innerHTML = workouts.map(w => `
        <div class="workout-item">
            <div class="workout-header">${w.type} - ${w.intensity} Intensity</div>
            <div class="workout-details">
                <span>⏱ ${w.duration} min</span>
                <span>📅 ${w.timestamp}</span>
                ${w.notes ? `<br><span>📝 ${w.notes}</span>` : ''}
            </div>
            <button class="delete-btn" onclick="deleteWorkout('${w.id}')">[ DELETE ]</button>
        </div>
    `).join('');
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const workoutData = {
        type: document.getElementById('workoutType').value,
        duration: parseInt(document.getElementById('duration').value),
        intensity: document.getElementById('intensity').value,
        notes: document.getElementById('notes').value
    };

    const success = await logWorkout(workoutData);
    
    if (success) {
        form.reset();
    }
});

loadBtn.addEventListener('click', loadWorkouts);

window.addEventListener('load', () => {
    showStatus('✓ Connected to server');
    loadWorkouts();
});