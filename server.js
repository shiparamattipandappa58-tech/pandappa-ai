const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Configure Twilio Client
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const twilioNumber = process.env.TWILIO_WHATSAPP_NUMBER || 'whatsapp:+14155238886';

let twilioClient = null;
if (accountSid && authToken && accountSid !== 'your_twilio_account_sid_here') {
    const twilio = require('twilio');
    twilioClient = twilio(accountSid, authToken);
}

// In-Memory Database Simulation
const database = {
    students: [],
    attendanceLogs: []
};

// --- ROUTE 1: Student Registration (Pending Approval) ---
app.post('/api/student/register', (req, res) => {
    try {
        const { fullName, rollNumber, course, semester, studentPhone, parentPhone, password } = req.body;

        if (!fullName || !rollNumber || !course || !studentPhone || !parentPhone || !password) {
            return res.status(400).json({ success: false, message: 'ದಯವಿಟ್ಟು ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ.' });
        }

        const existingUser = database.students.find(s => s.studentPhone === studentPhone);
        if (existingUser) {
            return res.status(400).json({ success: false, message: 'ಈ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಈಗಾಗಲೇ ನೋಂದಾಯಿಸಲ್ಪಟ್ಟಿದೆ.' });
        }

        const newStudent = {
            id: Date.now().toString(),
            fullName,
            rollNumber,
            course,
            semester,
            studentPhone,
            parentPhone,
            password,
            status: 'PENDING'
        };

        database.students.push(newStudent);

        return res.status(201).json({
            success: true,
            message: 'ನೋಂದಣಿ ಯಶಸ್ವಿಯಾಗಿದೆ! ಪ್ರಿನ್ಸಿಪಾಲರ ಅನುಮೋದನೆ ನಂತರ ಲಾಗಿನ್ ಆಗಬಹುದು.',
            student: newStudent
        });
    } catch (error) {
        return res.status(500).json({ success: false, error: error.message });
    }
});

// --- ROUTE 2: Get Pending Students for Principal Approval ---
app.get('/api/principal/pending-students', (req, res) => {
    const pending = database.students.filter(s => s.status === 'PENDING');
    res.status(200).json({ success: true, pendingStudents: pending });
});

// --- ROUTE 3: Principal Approve/Reject Student ---
app.put('/api/principal/approve/:studentId', (req, res) => {
    const { studentId } = req.params;
    const { action } = req.body; // 'APPROVE' or 'REJECT'

    const student = database.students.find(s => s.id === studentId);
    if (!student) {
        return res.status(404).json({ success: false, message: 'ವಿದ್ಯಾರ್ಥಿ ಪತ್ತೆಯಾಗಿಲ್ಲ.' });
    }

    if (action === 'APPROVE') {
        student.status = 'APPROVED';
        return res.status(200).json({ success: true, message: `${student.fullName} ಅವರ ಖಾತೆ ಅನುಮೋದನೆಗೊಂಡಿದೆ!` });
    } else {
        student.status = 'REJECTED';
        return res.status(200).json({ success: true, message: `${student.fullName} ಅವರ ಅರ್ಜಿ ತಿರಸ್ಕರಿಸಲ್ಪಟ್ಟಿದೆ.` });
    }
});

// --- ROUTE 4: Instant Real-Time WhatsApp Alert on Absent Click ---
app.post('/api/attendance/mark-absent', async (req, res) => {
    try {
        const { studentName, rollNumber, parentPhone } = req.body;

        if (!studentName || !parentPhone) {
            return res.status(400).json({ success: false, message: 'ವಿದ್ಯಾರ್ಥಿ ಹೆಸರು ಮತ್ತು ಪಾಲಕರ ಫೋನ್ ಸಂಖ್ಯೆ ಕಡ್ಡಾಯ.' });
        }

        const formattedPhone = parentPhone.startsWith('+') ? parentPhone : `+91${parentPhone}`;
        const messageBody = `ಗೌರವಾನ್ವಿತ ಪಾಲಕರೇ,\n\nನಿಮ್ಮ ಮಗ/ಮಗಳು *${studentName}* (Roll No: ${rollNumber}) ಇಂದು ಸರ್ಕಾರಿ ಪ್ರಥಮ ದರ್ಜೆ ಕಾಲೇಜು, ಬೈಂದೂರಿಗೆ ಗೈರುಹಾಜರಾಗಿದ್ದಾರೆ (ABSENT).\n\n- ಪ್ರಾಂಶುಪಾಲರು, GFGC ಬೈಂದೂರು.`;

        if (twilioClient) {
            await twilioClient.messages.create({
                from: twilioNumber,
                to: `whatsapp:${formattedPhone}`,
                body: messageBody
            });
            console.log(`[Twilio Sent] WhatsApp alert sent to ${formattedPhone}`);
        } else {
            console.log(`[Simulation Mode] WhatsApp message to ${formattedPhone}:\n${messageBody}`);
        }

        database.attendanceLogs.push({
            studentName,
            rollNumber,
            status: 'ABSENT',
            timestamp: new Date().toISOString()
        });

        return res.status(200).json({
            success: true,
            message: `${studentName} ಅವರ ಪಾಲಕರಿಗೆ ಆಟೋಮ್ಯಾಟಿಕ್ ವಾಟ್ಸಾಪ್ ಸಂದೇಶ ರವಾನೆಯಾಗಿದೆ.`
        });
    } catch (error) {
        console.error('WhatsApp Error:', error);
        return res.status(500).json({ success: false, error: 'ವಾಟ್ಸಾಪ್ ಸಂದೇಶ ಕಳುಹಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.' });
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`🚀 GFGC Server running at http://localhost:${PORT}`);
});
