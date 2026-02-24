// Get references to the HTML elements
const statusTextElement = document.getElementById('status-text');
const armedTextElement = document.getElementById('armed-text');
const toggleButtonElement = document.getElementById('toggle-button');
const logContainerElement = document.getElementById('log-container');
const passwordModal = document.getElementById('password-modal');
const modalPasswordInput = document.getElementById('modal-password-input');
const notificationBell = document.getElementById('notification-bell');

let sessionPassword = null;
let notificationsEnabled = false;
let wasTriggered = false; // To prevent multiple notifications

/**
 * Adds a new message to the log on the webpage.
 */
function addLogMessage(message) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('p');
    logEntry.textContent = `[${timestamp}] ${message}`;
    logContainerElement.prepend(logEntry);
}

/**
 * Fetches the current alarm status from the server and updates the UI.
 */
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Check for trigger state change to send notification
        if (data.is_triggered && !wasTriggered) {
            if (notificationsEnabled && Notification.permission === "granted") {
                new Notification("ALARM TRIGGERED!", {
                    body: "The security system has been activated.",
                    // You could add an icon here, e.g., icon: '/path/to/icon.png'
                });
            }
            wasTriggered = true;
        } else if (!data.is_triggered) {
            wasTriggered = false; // Reset when alarm is no longer triggered
        }

        // Update logs from server
        if (data.logs) {
            logContainerElement.innerHTML = '';
            data.logs.forEach(msg => {
                const p = document.createElement('p');
                p.textContent = msg;
                logContainerElement.appendChild(p);
            });
        }

        // Update the Armed status and Button
        if (data.is_running) {
            if (data.is_triggered) {
                statusTextElement.textContent = 'ALARM TRIGGERED!';
                statusTextElement.style.color = '#e74c3c'; // Red
            } else {
                statusTextElement.textContent = 'Monitoring...';
                statusTextElement.style.color = '#f39c12'; // Orange
            }

            armedTextElement.textContent = 'ARMED';
            armedTextElement.style.color = '#e74c3c'; // Red
            
            toggleButtonElement.textContent = 'Disarm';
            toggleButtonElement.className = 'disarm-button';
        } else {
            statusTextElement.textContent = 'Standby';
            statusTextElement.style.color = '#2ecc71'; // Green

            armedTextElement.textContent = 'DISARMED';
            armedTextElement.style.color = '#2ecc71'; // Green
            
            toggleButtonElement.textContent = 'Arm';
            toggleButtonElement.className = 'arm-button';
        }
    } catch (error) {
        console.error("Failed to fetch status:", error);
        statusTextElement.textContent = 'OFFLINE';
        statusTextElement.style.color = 'grey';
        armedTextElement.textContent = 'Unknown';
        armedTextElement.style.color = 'grey';
    }
}

/**
 * Asks for permission and toggles browser notifications.
 */
async function toggleNotifications() {
    // Browsers require a secure context (HTTPS or localhost) for notifications.
    if (!window.isSecureContext) {
        alert("Browser notifications are disabled on insecure connections. This feature only works on 'localhost' or sites with HTTPS.");
        return;
    }

    if (!("Notification" in window)) {
        alert("This browser does not support desktop notifications.");
        return;
    }

    // If permission is already granted, just toggle the state
    if (Notification.permission === "granted") {
        notificationsEnabled = !notificationsEnabled;
    } else if (Notification.permission !== "denied") {
        // Otherwise, we need to ask for permission
        const permission = await Notification.requestPermission();
        if (permission === "granted") {
            notificationsEnabled = true;
            new Notification("Notifications Enabled!", {
                body: "You will now be notified when the alarm is triggered.",
            });
        }
    }

    // Update bell style based on the final state
    notificationBell.style.opacity = notificationsEnabled ? '1' : '0.5';
    notificationBell.style.color = notificationsEnabled ? '#f1c40f' : ''; // Yellow when on
}

/**
 * Saves the password from the modal and retries the action.
 */
function submitPassword() {
    const input = modalPasswordInput.value;
    if (input) {
        sessionPassword = input;
        passwordModal.style.display = "none";
    }
}

/**
 * Clears the server-side logs.
 */
async function clearLogs() {
    if (!sessionPassword) {
        passwordModal.style.display = "block";
        modalPasswordInput.focus();
        return;
    }
    try {
        await fetch('/api/logs/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: sessionPassword })
        });
        // Status update will happen automatically on next poll
    } catch (e) {
        console.error(e);
    }
}

/**
 * Handles the button click to toggle the alarm state.
 */
async function toggleState() {
    try {
        if (!sessionPassword) {
            passwordModal.style.display = "block";
            modalPasswordInput.focus();
            return;
        }

        toggleButtonElement.disabled = true; // Prevent multiple clicks

        const response = await fetch('/api/toggle', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: sessionPassword })
        });
        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                sessionPassword = null; // Reset password if incorrect
                addLogMessage("Error: Incorrect Password.");
                passwordModal.style.display = "block"; // Show modal again
                modalPasswordInput.value = '';
                modalPasswordInput.focus();
                return;
            }
            const errorMessage = data.error || `Request failed with status: ${response.status}`;
            throw new Error(errorMessage);
        }

        // Update UI immediately
        await updateStatus();

    } catch (error) {
        console.error("Failed to toggle alarm state:", error.message);
        addLogMessage(`Error: ${error.message}`);
    } finally {
        toggleButtonElement.disabled = false;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    updateStatus();

    // Visually disable notifications if not on a secure context like localhost or https
    if (!window.isSecureContext) {
        notificationBell.style.opacity = '0.2';
        notificationBell.style.cursor = 'not-allowed';
    }

    // Show password modal on load
    passwordModal.style.display = "block";
    modalPasswordInput.focus();

    // Check status every 2 seconds
    setInterval(updateStatus, 2000);
});