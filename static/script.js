//  TC ID Göster/Gizle Butonu
document.addEventListener('DOMContentLoaded', () => {
    const toggleTcID = document.getElementById('toggleTcID');
    const tcIDInput = document.getElementById('tcID');

    if (toggleTcID && tcIDInput) {
        toggleTcID.addEventListener('click', () => {
            if (tcIDInput.type === 'password') {
                tcIDInput.type = 'text';
                toggleTcID.textContent = '🔒'; // Şifreyi gizle simgesi
            } else {
                tcIDInput.type = 'password';
                toggleTcID.textContent = '👁️'; // Şifreyi göster simgesi
            }
        });
    }
});


document.addEventListener('DOMContentLoaded', () => {
    const appointmentForm = document.getElementById('appointmentForm');

    if (appointmentForm) {
        appointmentForm.addEventListener('submit', registerCustomer);
    } else {
        console.error('Form not found: appointmentForm');
    }

    // Sayfa yüklendiğinde randevuları getir
    fetchAppointments();
});

// Kullanıcı Kayıt ve Randevu Ekleme Fonksiyonu
async function registerCustomer(event) {
    event.preventDefault();

    const tcID = document.getElementById('tcID').value;
    const customerName = document.getElementById('customerName').value;
    const customerSurname = document.getElementById('customerSurname').value;
    const birthYear = document.getElementById('birthYear').value;
    const appointmentDate = document.getElementById('appointmentDate').value;
    const appointmentTime = document.getElementById('appointmentTime').value;

    if (!tcID || !customerName || !customerSurname || !birthYear || !appointmentDate || !appointmentTime) {
        alert('All fields are required!');
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tcID,
                customerName,
                customerSurname,
                birthYear,
                appointmentDate,
                appointmentTime
            })
        });

        const result = await response.json();
        if (response.ok) {
            alert('Customer registered successfully!');
            fetchAppointments(); // Listeyi güncelle
            document.getElementById('appointmentForm').reset();
        } else {
            alert(`Error: ${result.error}`);
            console.error('Backend Error:', result.error);
        }
    } catch (error) {
        console.error('Error registering customer:', error);
    }
}

// Randevuları Getir ve Görüntüle
async function fetchAppointments() {
    try {
        const response = await fetch('http://localhost:8000/appointments');
        if (!response.ok) {
            throw new Error('Failed to fetch appointments');
        }

        const appointments = await response.json();
        const tableBody = document.getElementById('appointmentTableBody');
        tableBody.innerHTML = ''; // Mevcut tabloyu temizle

        appointments.forEach(appointment => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${appointment.id}</td>
                <td>******</td> <!-- TC ID asla gösterilmez -->
                <td>${appointment.customerName}</td>
                <td>${appointment.customerSurname}</td>
                <td>${appointment.birthYear}</td>
                <td>${appointment.appointmentDate || 'N/A'}</td>
                <td>${appointment.appointmentTime || 'N/A'}</td>
                <td>
                    <button class="delete-btn" onclick="deleteAppointment(${appointment.id})">🗑️ Delete</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching appointments:', error);
    }
}

//Randevu Silme Fonksiyonu
async function deleteAppointment(appointmentId) {
    try {
        const response = await fetch(`http://localhost:8000/delete_appointment/${appointmentId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.error || 'Failed to delete appointment');
        }

        alert('Appointment deleted successfully!');
        fetchAppointments(); // Tabloyu güncelle
    } catch (error) {
        console.error('Error deleting appointment:', error);
        alert(`Error: ${error.message}`);
    }


}
