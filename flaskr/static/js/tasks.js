$(document).ready(function () {
    // 1. figure out the default (mirrors what Jinja already picked)
    let currentProjectId = $(".project-card").first().data("project");
    let currentMembers = [];

    // 2. for viewing different projects / reusable function
    function loadTasks(projectId) {
        if (!projectId) {
            $("tbody").empty();
            return;
        }

        $.ajax({
            url: "/api/tasks/" + projectId,
            method: "GET",
            success: function (response) {
                $("tbody").empty(); // 1. clear old rows
                currentMembers = response.members ?? [];

                response.tasks.forEach(function (task, index) {  // 2. loop through each task
                    $("tbody").append(buildTaskRow(task, index + 1, currentMembers));
                });
                $("tbody select[data-task-id]").each(function () { updateStatusColor(this); });
                $("#deleteTasksBtn").addClass("hidden");
                populateOwnerDropdown(currentMembers);
            }
        });
    }

    // 3. call it immediately "on page load"
    loadTasks(currentProjectId);

    // 4. Polling to check if others have updated tasks. 30000ms = 30 seconds
    setInterval(function () {
        const anyChecked = $("tbody input[type='checkbox']:checked").length > 0;
        if (currentProjectId && !anyChecked) {
            loadTasks(currentProjectId);
        }
    }, 30000);


    // 5. click handler, unchanged except it also calls loadTasks
    $(".project-card").on("click", function () {
        currentProjectId = $(this).data("project");
        $(".project-card").removeClass("border-2 border-emerald-300 bg-emerald-50").addClass("border");
        $(this).removeClass("border").addClass("border-2 border-emerald-300 bg-emerald-50");
        loadTasks(currentProjectId);
    });

    // open modal
    $("#newTaskBtn").on("click", function () {
        if (!currentProjectId) {
            alert("프로젝트를 먼저 선택해주세요.");
            return;
        }
        $("#taskModal").removeClass("hidden");
    });

    // close modal (cancel button, or clicking the dark overlay)
    $("#closeModalBtn, #taskModal").on("click", function (e) {
        if (e.target.id === "closeModalBtn" || e.target.id === "taskModal") {
            $("#taskModal").addClass("hidden");
            $("#taskModal input").val(""); // clear form fields on close
            $("#taskOwner").val("");
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
        const task = {
            project_id: currentProjectId,
            agenda: $("#taskAgenda").val().trim(),
            due_date: $("#taskDueDate").val(),
            owner: $("#taskOwner").val().trim(),
            status: "not-started"
        };

        if (!task.project_id || !task.agenda || !task.due_date || !task.owner) {
            alert("모든 항목을 기재해주세요.");
            return;
        }

        $.ajax({
            url: "/api/tasks",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(task),
            success: function (newTask) {
                const rowCount = $("tbody tr").length + 1;
                $("tbody").append(buildTaskRow(newTask, rowCount, currentMembers));
                updateStatusColor($("tbody tr:last select[data-task-id]")[0]);
                $("#taskModal").addClass("hidden");
                $("#taskModal input").val("");
                $("#taskOwner").val("");
            },
            error: function (xhr) {
                alert(xhr.responseJSON?.error || "태스크 저장에 실패했습니다.");
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

        if (!confirm(`선택한 태스크 ${idsToDelete.length}개를 삭제하시겠습니까?`)) return;

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

    $(document).on("change", ".task-field", function () {
        const $field = $(this);
        const value = $field.val().trim();

        if (!value) {
            alert("빈 값으로 수정할 수 없습니다.");
            loadTasks(currentProjectId);
            return;
        }

        $.ajax({
            url: "/api/tasks/" + $field.closest("tr").data("task-id"),
            method: "PATCH",
            contentType: "application/json",
            data: JSON.stringify({ [$field.data("field")]: value }),
            error: function () {
                alert("태스크 수정에 실패했습니다.");
                loadTasks(currentProjectId);
            }
        });
    });


});

function populateOwnerDropdown(members) {
    const $select = $("#taskOwner").empty();
    $("<option>").val("").text("담당자를 선택하세요").appendTo($select);

    members.forEach(function (member) {
        if (!member.name) return;
        const label = member.email ? `${member.name} (${member.email})` : member.name;
        $("<option>").val(member.name).text(label).appendTo($select);
    });
}

function buildTaskRow(task, index, members) {
    const agenda = escapeAttribute(task.agenda);
    const dueDate = escapeAttribute(task.due_date);
    const ownerOptions = buildOwnerOptions(members, task.owner);

    return `
    <tr class="border-b" data-task-id="${task._id}">
      <td class="py-3 pl-3"><input type="checkbox"></td>
      <td class="py-3 text-gray-400">${index}</td>
      <td class="py-3">
        <input type="text" value="${agenda}" data-field="agenda" aria-label="태스크 내용"
               class="task-field w-full rounded border border-transparent bg-transparent px-1 outline-none hover:border-gray-300 focus:border-emerald-500 focus:bg-white">
      </td>
      <td class="py-3">
        <input type="date" value="${dueDate}" data-field="due_date" aria-label="태스크 기한"
               class="task-field rounded border border-transparent bg-transparent px-1 outline-none hover:border-gray-300 focus:border-emerald-500 focus:bg-white">
      </td>
      <td class="py-3">
        <select data-field="owner" aria-label="태스크 담당자"
                class="task-field w-full rounded border border-transparent bg-transparent px-1 outline-none hover:border-gray-300 focus:border-emerald-500 focus:bg-white">
          ${ownerOptions}
        </select>
      </td>
      <td class="py-3">
        <select class="rounded-full border-0 px-3 py-1 text-xs font-medium"
                data-task-id="${task._id}"
                onchange="updateStatusColor(this); updateTaskStatus(this);">
          <option value="not-started" ${task.status === "not-started" ? "selected" : ""}>시작 전</option>
          <option value="in-progress" ${task.status === "in-progress" ? "selected" : ""}>진행 중</option>
          <option value="done" ${task.status === "done" ? "selected" : ""}>완료</option>
        </select>
      </td>
    </tr>
  `;
}

function escapeAttribute(value) {
    const entities = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
    return String(value ?? "").replace(/[&<>"']/g, character => entities[character]);
}

function buildOwnerOptions(members, currentOwner) {
    const options = [...(members ?? [])];
    if (currentOwner && !options.some(member => member.name === currentOwner)) {
        options.unshift({ name: currentOwner });
    }

    return options
        .filter(member => member.name)
        .map(function (member) {
            const selected = member.name === currentOwner ? " selected" : "";
            const label = member.email ? `${member.name} (${member.email})` : member.name;
            return `<option value="${escapeAttribute(member.name)}"${selected}>${escapeAttribute(label)}</option>`;
        })
        .join("");
}

function updateTaskStatus(select) {
    $.ajax({
        url: "/api/tasks/" + $(select).data("task-id"),
        method: "PATCH",
        contentType: "application/json",
        data: JSON.stringify({ status: select.value }),
        error: function () {
            alert("상태 저장에 실패했습니다.");
        }
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
