$(document).ready(function () {
    // 1. figure out the default (mirrors what Jinja already picked)
    let currentProjectId = $(".project-card").first().data("project");

    if (currentProjectId) {
        loadTasks(currentProjectId);
    } else {
        $("tbody").empty();
    }

    // 2. for viewing different projects / reusable function
    function loadTasks(projectId) {
        $.ajax({
            url: "/api/tasks/" + projectId,
            method: "GET",
            success: function (tasks) {
                $("tbody").empty(); // 1. clear old rows

                tasks.forEach(function (task, index) {  // 2. loop through each task
                    $("tbody").append(buildTaskRow(task, index + 1));
                    $("tbody select").each(function () { updateStatusColor(this) });
                });
                $("#deleteTasksBtn").addClass("hidden");
            }
        });
    }

    // 4. Polling to check if others have updated tasks. 30000ms = 30 seconds
    setInterval(function () {
        const anyChecked = $("tbody input[type='checkbox']:checked").length > 0;
        if (!anyChecked) {
            loadTasks(currentProjectId);
        }
    }, 30000);


    // 5. click handler, unchanged except it also calls loadTasks
    $(".project-card").on("click", function () {
        currentProjectId = $(this).data("project");
        $(".project-card").removeClass("border-2 bg-emerald-50").addClass("border");
        $(this).removeClass("border").addClass("border-2 bg-emerald-50");
        loadTasks(currentProjectId);
    });




    // open modal
    $("#newTaskBtn").on("click", function () {
        if (!currentProjectId) {
            alert("Select a project first");
            return;
        }
        $("#taskModal").removeClass("hidden");
    });

    // close modal (cancel button, or clicking the dark overlay)
    $("#closeModalBtn, #taskModal").on("click", function (e) {
        if (e.target.id === "closeModalBtn" || e.target.id === "taskModal") {
            $("#taskModal").addClass("hidden");
            $("#taskModal input").val(""); // clear form fields on close
        }
    });

    // stop clicks inside the modal box from bubbling up and closing it
    $("#taskModal > div").on("click", function (e) {
        e.stopPropagation();
    });

    $("#submitTask").on("click", function () {
        addTask();
    });



    function addTask() {

        // Validation Check ———————————————————————————————————————————————————
        // 1) In case there is no project 
        if (!currentProjectId) {
            alert("프로젝트를 먼저 추가해주세요.");
            return;
        }
        // 2) In case user input is invalid 
        if (!task.agenda || !task.due_date || !task.owner) {
            alert("모든 항목을 기재해주세요.");
            return;
        }

        const task = {
            project_id: currentProjectId,
            agenda: $("#taskAgenda").val(),
            due_date: $("#taskDueDate").val(),
            owner: $("#taskOwner").val(),
            status: "not-started"   // pick ONE casing/format and use it everywhere
        };

        $.ajax({
            url: "/api/tasks",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(task),
            success: function (newTask) {
                const rowCount = $("tbody tr").length + 1;
                $("tbody").append(buildTaskRow(newTask, rowCount));
                updateStatusColor($("tbody tr:last select")[0]);
                $("#taskModal").addClass("hidden");
                $("#taskModal input").val("");
            },
            // 3) If backend server responds with error, alert user
            error: function (xhr) {
                alert(xhr.responseJSON?.error || "Something went wrong.");
            }
        });
    }

    $(document).on("change", "tbody input[type='checkbox']", function () {
        // grey out this specific row if checked
        $(this).closest("tr").toggleClass("bg-gray-100", this.checked);

        // show delete button only if at least one checkbox is checked
        const anyChecked = $("tbody input[type='checkbox']:checked").length > 0;
        $("#deleteTasksBtn").toggleClass("hidden", !anyChecked);
    });



    $("#deleteTasksBtn").on("click", function () {
        const idsToDelete = [];

        $("tbody input[type='checkbox']:checked").each(function () {
            idsToDelete.push($(this).closest("tr").data("task-id"));
        });

        if (!confirm(`Delete ${idsToDelete.length} task(s)?`)) return;

        $.ajax({
            url: "/api/tasks",
            method: "DELETE",
            contentType: "application/json",
            data: JSON.stringify({ task_ids: idsToDelete }),
            success: function () {
                $("tbody input[type='checkbox']:checked").closest("tr").remove();
                $("#deleteTasksBtn").addClass("hidden");
            }
        });
    });


    $(document).on("blur", ".task-field", function () {
        const taskId = $(this).closest("tr").data("task-id");
        const field = $(this).data("field");
        const value = $(this).val();

        $.ajax({
            url: "/api/tasks/" + taskId,
            method: "PATCH",
            contentType: "application/json",
            data: JSON.stringify({ [field]: value })
        });
    });
});

function buildTaskRow(task, index) {
    return `
    <tr class="border-b" data-task-id="${task._id}">
       <td class="py-3 pl-3"><input type="checkbox"></td>
       <td class="py-3 text-gray-400">${index}</td>
      

       <td class="py-3">
            <input type="text" value="${task.agenda}" 
            class="task-field bg-transparent border border-transparent hover:border-gray-300 focus:border-emerald-500 focus:bg-white rounded px-1 outline-none w-full"
            data-field="agenda">
       </td>
       
        <td class="py-3">
            <input type="date" value="${task.due_date}" 
            class="task-field bg-transparent border border-transparent hover:border-gray-300 focus:border-emerald-500 focus:bg-white rounded px-1 outline-none"
            data-field="due_date" data-task-id="${task._id}">
        </td>
       
       
       <td class="py-3">
            <input type="text" value="${task.owner}" 
            class="task-field bg-transparent border border-transparent hover:border-gray-300 focus:border-emerald-500 focus:bg-white rounded px-1 outline-none w-full"
            data-field="agenda">
       </td>

        <td class="py-3">
            <select class="rounded-full border-0 px-3 py-1 text-xs font-medium" 
                    onchange="updateStatusColor(this); updateTaskStatus(this);"
                    data-task-id="${task._id}">
                <option value="not-started" ${task.status === "not-started" ? "selected" : ""}>Not started</option>
                <option value="in-progress" ${task.status === "in-progress" ? "selected" : ""}>In progress</option>
                <option value="done" ${task.status === "done" ? "selected" : ""}>Done</option>
            </select>
        </td>
       
    </tr>
  `;
}


function updateTaskStatus(select) {
    const taskId = $(select).data("task-id");
    const newStatus = select.value;

    $.ajax({
        url: "/api/tasks/" + taskId,
        method: "PATCH",
        contentType: "application/json",
        data: JSON.stringify({ status: newStatus })
    });
}


function updateStatusColor(select) {
    select.classList.remove(
        "bg-red-100", "text-red-700",
        "bg-yellow-100", "text-yellow-700",
        "bg-green-100", "text-green-700"
    );

    const colors = {
        "not-started": ["bg-red-100", "text-red-700"],
        "in-progress": ["bg-yellow-100", "text-yellow-700"],
        "done": ["bg-green-100", "text-green-700"]
    };

    select.classList.add(...colors[select.value]);
}
