const url = "35.212.253.73:5050";


async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const hash = CryptoJS.SHA256(password).toString(CryptoJS.enc.Hex);
    const response = await fetch(`http://${url}/login/?username=${username}&password=${hash}`)
    const res = await response.json()
    if (response.ok) {
        localStorage.setItem("sid", res["sid"]);
        console.log(localStorage.getItem("sid"))
        window.location.href = 'Main.html';
    }
    else { 
        document.getElementById('errorMessage').style.display = 'block';
        console.log(res["message"])
    }
}



async function register(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const code = document.getElementById('verificationCode').value;
    if (password !== confirmPassword) {
        document.getElementById('errorMessage').textContent = 'Passwords do not match.';
        document.getElementById('errorMessage').style.display = 'block';
        return;
    }
    const hash = CryptoJS.SHA256(password).toString(CryptoJS.enc.Hex);
    const response = await fetch(`http://${url}/register/?username=${username}&email=${email}&password=${hash}&code=${code}`)
    if (response.ok) {
        alert("Registered!")
        const loginres = await fetch(`http://${url}/login/?username=${username}&password=${hash}`)
        if (loginres.ok) {
            var js = await loginres.json();
            localStorage.setItem("sid", js["sid"]);
            window.location.href = "Main.html";
        }
        else {
            document.getElementById('errorMessage').textContent = "Something went wrong logging you in.";
            document.getElementById('errorMessage').style.display = 'block';
    
        }
    }
    else if (response.status == 500) {
        document.getElementById('errorMessage').textContent = "Username/Email already exists.";
        document.getElementById('errorMessage').style.display = 'block';

    }
    else {
        const js = await response.json();
        document.getElementById('errorMessage').textContent = js["message"];
        document.getElementById('errorMessage').style.display = 'block';

    }
}


async function sendCode() {
    const email = document.getElementById('email').value;
    const response = await fetch(`http://${url}/code/?email=${email}`)
    if (response.ok) {
        alert("Code sent to your mail box");
    }
    else {
        alert("Something went wrong");
    }
}


async function logout() {
    const response = await fetch(`http://${url}/logout/?sid=${localStorage.getItem("sid")}`)
    if (response.status == 200) {
        alert("Logged out");
        localStorage.removeItem("sid");
    }
    else if (response.status == 401) {
        alert("Already logged out");
    }
    else {
        alert("Something went wrong")
    }
    window.location.href = "index.html";
}



async function handleResetPassword(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const verificationCode = document.getElementById('verificationCode').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (newPassword !== confirmPassword) {
        document.getElementById('errorMessage').textContent = 'Passwords do not match.';
        document.getElementById('errorMessage').style.display = 'block';
        return;
    }
    const hash = CryptoJS.SHA256(newPassword).toString(CryptoJS.enc.Hex);
    const response = await fetch(`http://${url}/reset/?code=${verificationCode}&email=${email}&password=${hash}`)
    if (response.ok) {
        alert("Password reset");
        logout();   
        localStorage.removeItem("sid");
        window.location.href = "index.html";
    }
    else {
        const js = await response.json();
        document.getElementById('errorMessage').textContent = js["message"];
        document.getElementById('errorMessage').style.display = 'block';
    }

}


async function addTask(event) {
    event.preventDefault();
    const taskName = document.getElementById('taskName').value;
    const description = document.getElementById('description').value;
    const category = document   .getElementById('category').value;
    const dueDate = document.getElementById('dueDate').value;
    var t = new Date(dueDate);
    t = Math.floor(t.getTime()/1000);
    const response = await fetch(`http://${url}/add/?sid=${localStorage.getItem("sid")}&title=${taskName}&desc=${description}&category=${category}&due=${t}`);
    if (response.ok) {
        alert('Task added successfully!');
        window.location.href = 'Main.html';
    }
    else if (response.status == 401) {
        alert("Session invalid. Please login again")
        window.location.href = "index.html";
    }
    else {
        alert("Something went wrong")
    }
}



async function listAllTasks(completed) {
    const response = await fetch(`http://${url}/get/?sid=${localStorage.getItem("sid")}`);
    const res = await response.json();
    console.log(res)
    if (response.ok) {
        var tasks = res["tasks"];
        tasks.forEach(task => {
            const taskList = document.getElementById("taskList");
            const taskDiv = document.createElement('div');
            taskDiv.className = 'task';
            task[4] = new Date(Number(task[4])*1000).toLocaleString("en-GB");
            console.log(task[4])
            if (task[5] == 1) {
                taskDiv.classList.add('completed');
            }
            taskDiv.innerHTML = `
                <p><strong>Task Name:</strong> ${task[1]}</p>
                <p><strong>Description:</strong> ${task[2]}</p>
                <p><strong>Category:</strong> ${task[3]}</p>
                <p><strong>Due Date:</strong> ${task[4]}</p>
            `;
            taskList.appendChild(taskDiv);
        });

        if (tasks.length === 0) {
            taskList.innerHTML = '<p>No tasks found.</p>';
        }

    }
    else if (response.status == 401) {
        alert("Session invalid. Please login again.")
        window.location.href = "index.html";
    }
    else {
        alert("Something went wrong")
    }
}


async function listUncompletedTasks() {
    const taskList = document.getElementById("taskList");
    const response = await fetch(`http://${url}/get/?sid=${localStorage.getItem("sid")}&uncompleted=1`);
    const res = await response.json();
    console.log(res)
    if (response.ok) {
        var tasks = res["tasks"];
        tasks.forEach(task => {
            const taskList = document.getElementById("taskList");
            const taskDiv = document.createElement('div');
            taskDiv.className = 'task';
            task[4] = new Date(Number(task[4])*1000).toLocaleString("en-GB");
            console.log(task[4])
            taskDiv.innerHTML = `
                <p><strong>Task Name:</strong> ${task[1]}</p>
                <p><strong>Description:</strong> ${task[2]}</p>
                <p><strong>Category:</strong> ${task[3]}</p>
                <p><strong>Due Date:</strong> ${task[4]}</p>
            `;
            taskList.appendChild(taskDiv);
        });

        if (tasks.length === 0) {
            taskList.innerHTML = '<p>No tasks found.</p>';
        }

    }
    else if (response.status == 401) {
        alert("Session invalid. Please login again.")
        window.location.href = "index.html";
    }
    else {
        alert("Something went wrong")
    }
}



async function setTaskCompleted() {
    const response = await fetch(`http://${url}/get/?sid=${localStorage.getItem("sid")}&uncompleted=1`);
    const res = await response.json();
    if (response.ok) {
        var tasks = res["tasks"];
        tasks.forEach(task => {
            console.log(task); 
            const taskList = document.getElementById("taskList");
            const taskDiv = document.createElement('div');
            taskDiv.className = 'task';
            task[4] = new Date(Number(task[4])*1000).toLocaleString("en-GB");
            console.log(task[4])
            taskDiv.innerHTML = `
                <p><strong>Task Name:</strong> ${task[1]}</p>
                <p><strong>Description:</strong> ${task[2]}</p>
                <p><strong>Category:</strong> ${task[3]}</p>
                <p><strong>Due Date:</strong> ${task[4]}</p>
                <button onclick="markAsCompleted(${task[0]})">Mark as Completed</button>
            `;
            taskList.appendChild(taskDiv);
        });

        if (tasks.length === 0) {
            taskList.innerHTML = '<p>No tasks found.</p>';
        }
    }
    else if (response.status == 401) {
        alert("Session invalid. Please login again.")
        window.location.href = "index.html";
    }
    else {
        alert("Something went wrong")
    }
}



async function markAsCompleted(index) {
    const response = await fetch(`http://${url}/edit/?setcomplete=1&sid=${localStorage.getItem("sid")}&id=${index}`)
    if (response.ok) {
        alert("Task marked as complete.")
        location.reload()
    }
    else if (response.status == 401) {
        alert("Session invalid. Please login again")
    }
    else {
        alert("Something went wrong")
    }
}


async function editDeleteTask() {
    const response = await fetch(`http://${url}/get/?sid=${localStorage.getItem("sid")}`);
    const res = await response.json();
    if (response.ok) {
        var tasks = res["tasks"];
        tasks.forEach(task => {
            const taskList = document.getElementById("taskList");
            const taskDiv = document.createElement('div');
            taskDiv.className = 'task';
            task[4] = new Date((Number(task[4])*1000)+3600000*8).toISOString();
            taskDiv.innerHTML = `
                <form id="addTaskForm">
                    <div class="form-group">
                        <label for="taskName${task[0]}">Task Name:</label>
                        <input type="text" id="taskName${task[0]}" name="taskName" value="${task[1]}">
                    </div>
                    <div class="form-group">
                        <label for="description${task[0]}">Description:</label>
                        <textarea id="description${task[0]}" name="description" rows="4">${task[2]}</textarea>
                    </div>
                    <div class="form-group">
                        <label for="category${task[0]}">Category</label>
                        <select id="category${task[0]}" name="category">
                            <option value="${task[3]}" selected>${task[3]}</option>
                            <option value="Personal">Personal</option>
                            <option value="School">School</option>
                            <option value="Work">Work</option>
                            <option value="Others">Others</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="dueDate${task[0]}">Due Date:</label>
                        <input type="datetime-local" id="dueDate${task[0]}" name="dueDate" required value="${task[4].slice(0,-2)}">
                    </div>
                    </form>
                    <button onclick="editTask(${task[0]})">Edit Task</button>
                    <button onclick="deleteTask(${task[0]})" class="delete-button">Delete Task</button>
            `;
            taskList.appendChild(taskDiv);
        });

        if (tasks.length === 0) {
            taskList.innerHTML = '<p>No tasks found.</p>';
        }
    }
    else if (response.status == 401) {
        alert("Session invalid. Please login again.")
        window.location.href = "index.html";
    }
    else {
        alert("Something went wrong")
    }
};

async function editTask(index) {
    const taskName = document.getElementById(`taskName${index}`).value;
    const description = document.getElementById(`description${index}`).value;
    const category = document.getElementById(`category${index}`).value;
    const dueDate = document.getElementById(`dueDate${index}`).value;
    var t = new Date(dueDate);
    t = Math.floor(t.getTime()/1000);
    const response = await fetch(`http://${url}/edit/?sid=${localStorage.getItem("sid")}&id=${index}&title=${taskName}&desc=${description}&category=${category}&due=${t}`)
    if (response.ok) {
        alert("Task edited");
        location.reload();
    }
    else if (response.status == 401) {
        alert("Session invalid. Please login again")
        window.location.href = "index.html";
    }
    else {
        alert("Something went wrong")
    }
    
}

async function deleteTask(index) {
    const response = await fetch(`http://${url}/delete/?sid=${localStorage.getItem("sid")}&id=${index}`)
    if (response.ok) {
        alert("Task deleted")
        location.reload()
    }
    else if (response.status == 401) {
        alert("Session invalid. Please login again")
        window.location.href = "index.html";
    }    
    else {
        alert("Something went wrong")
    }
}

async function deleteCompletedTask() {
    const response = await fetch(`http://${url}/delete/?completed=1&sid=${localStorage.getItem("sid")}`)
    if (response.ok) {
        alert("Deleted successfully!")
        location.reload()
    }
    else if (response.status == 401) {
        alert("Session invalid. Please login again")
    }
    else {
        alert("Something went wrong")
    }
}