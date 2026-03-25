let tasks = JSON.parse(localStorage.getItem('tasks')) || [];
let filter = 'all';
let debounceTimer = null;

function addTask() {
    let title = document.getElementById('taskInput').value;
    let priority = document.getElementById('priorityInput').value;
    let dueDate = document.getElementById('dueDateInput').value;

    if (title === "") {
        alert("Please enter a task name");
        return;
    }

    let task = {
        title: title,
        priority: priority,
        date: dueDate,
        completed: false
    };

    tasks.push(task);
    saveTasks();
    renderTasks();

    document.getElementById('taskInput').value = "";
}

function saveTasks() {
    localStorage.setItem('tasks', JSON.stringify(tasks));
}

function deleteTask(index) {
    tasks.splice(index, 1);
    saveTasks();
    renderTasks();
}

function toggleTask(index) {
    tasks[index].completed = !tasks[index].completed;
    saveTasks();
    renderTasks();
}

function filterTasks(type) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
        filter = type;
        renderTasks();
    }, 300);
}

function sortPriority() {
    let map = { high: 3, medium: 2, low: 1};

    tasks.sort(function(a,b){
        return map[b.priority] - map[a.priority];
    });

    renderTasks();
}

function sortDeadline() {
    tasks.sort(function(a,b){
        return new Date(a.date) - new Date(b.date);
    });
    renderTasks();
}

function renderTasks() {
    let list = document.getElementById('taskList');
    list.innerHTML = "";

    let today = new Date();

    tasks.forEach(function (task, index) {

        if (filter === 'completed' && !task.completed) return;
        if (filter === 'pending' && task.completed) return;

        let badgeClass = "bg-success";

        if (task.priority === "medium") badgeClass = "bg-warning";
        if (task.priority === "high") badgeClass = "bg-danger";

        let overdueClass = "";
        if (task.date && new Date(task.date) < today && !task.completed) {
            overdueClass = "overdue";
        }

        let completedClass = task.completed ? "text-decoration-line-through text-muted" : "";

        list.innerHTML += `
        <div class="card mb-2 ${overdueClass}">
        <div class="card-body d-flex justify-content-between align-items-center">
        <div class="${completedClass}">
        <h5>${task.title}</h5>
        <span class="badge ${badgeClass}">${task.priority}</span>
        <small> ${task.date}</small>
        </div>
        <div>
        <button onClick="toggleTask(${index})" class="btn btn-success btn-sm">Completed</button>
        <button onClick="deleteTask(${index})" class="btn btn-danger btn-sm">Delete</button>
        </div>
        </div>
        </div>
        `;
    });

    document.getElementById("total").innerText = tasks.length;
    document.getElementById("completed").innerText = tasks.filter(t => t.completed).length;
    document.getElementById("pending").innerText = tasks.filter(t => !t.completed).length;
}

renderTasks();