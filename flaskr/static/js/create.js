let selectedMembers = initialMembers
let lastSearchedResults = []

const addedMember = $("#added-member")
const titleInput = $("#title");
const startDateInput = $("#start_date")
const endDateInput = $("#end_date")
const submitBtn = $("#submit-btn")
const searchBTN = $("#search-member")
const searchbox = $("#search-box")
const searchResult = $("#search-result")

//필수 입력 필드 다 채워졌는지 확인하고 버튼 상태 결정 (필수 입력: 프로젝트 타이틀, 기간)
function checkRequiredFields() {
const isTitleFilled = $("#title").val().trim() !== "";
const isStartDateFilled = $("#start_date").val().trim() !== "";
const isEndDateFilled  = $("#end_date").val().trim() !== "";

    if (isTitleFilled && isStartDateFilled && isEndDateFilled) {
        submitBtn.prop("disabled", false)
    }
    else {
        submitBtn.prop("disabled", true)
    }
}
titleInput.on("input", checkRequiredFields)
startDateInput.on("input", checkRequiredFields) 
startDateInput.on("input", function() {
    endDateInput.attr("min", startDateInput.val())
})
endDateInput.on("input", checkRequiredFields)

checkRequiredFields();
renderSelectedMembers()
//팀원 검색

function searchMember() {
    const searchValue = searchbox.val()
    const url = `/api/users/search?search_member=${searchValue}`
    $.ajax({
        url: url,
        method: "GET",
        success: function (data) {
            lastSearchedResults = data
            renderSearchResults()
        }
    })
}

function renderSearchResults() {
    searchResult.empty()
    if (lastSearchedResults.length === 0) {
        searchResult.append("<div class=\"px-3 py-2 text-gray-400\">검색 결과가 없습니다.</div>")
    } else {
        lastSearchedResults.forEach(user => {
            const isAdded = selectedMembers.some(member => member.email === user.email)
            const buttonHtml = isAdded
                ? `<span class="text-gray-300 text-xs font-medium">추가됨</span>`
                : `<button type="button" class="text-emerald-600 hover:text-emerald-700 text-xs font-medium" onclick="addMember('${user.name}', '${user.email}')">+ 추가</button>`
            searchResult.append(`<div class="flex items-center justify-between px-3 py-2 hover:bg-gray-50"><span>${user.name} <span class="text-gray-400">- ${user.email}</span></span>${buttonHtml}</div>`)
        })
    }
}

function handleKeydown(event) {
    if (event.key == "Enter") {
        event.preventDefault()
        searchMember()
    }
}


function addMember(name, email) {
    selectedMembers.push({ name: name, email: email })
    renderSelectedMembers()
    renderSearchResults()
}

function renderSelectedMembers() {
    addedMember.empty()
    selectedMembers.forEach(member => {
        addedMember.append(`<span class="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 text-xs font-medium px-3 py-1 rounded-full">${member.name}<button type="button" class="text-emerald-400 hover:text-emerald-700" onclick="removeMember('${member.email}')">✕</button></span>`)
    })
    $("#members").val(JSON.stringify(selectedMembers))
}


function removeMember(email) {
    selectedMembers = selectedMembers.filter(member => member.email !== email)
    renderSelectedMembers()
    renderSearchResults()
}

searchBTN.on("click", searchMember)
searchbox.on("keydown", handleKeydown)