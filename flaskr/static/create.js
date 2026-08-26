let selectedMembers = []
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
endDateInput.on("input", checkRequiredFields)

checkRequiredFields();

//팀원 검색

function searchMember() {
    const searchValue = searchbox.val()
    const url = `/api/users/search?search_member=${searchValue}`
    $.ajax({
        url: url,
        method: "GET",
        success: function(data) {
            lastSearchedResults = data
            renderSearchResults()
        }
    })
}

function renderSearchResults() {
    searchResult.empty()
    if (lastSearchedResults.length === 0) {
        searchResult.append("<div>검색 결과가 없습니다.</div>")
    } else {
        lastSearchedResults.forEach(user => {
            const isAdded = selectedMembers.some(member => member.email === user.email)
            const buttonHtml = isAdded ? "" : `<button type="button" onclick="addMember('${user.name}', '${user.email}')">+추가</button>`
            searchResult.append(`<div>${user.name} - ${user.email} ${buttonHtml}</div>`)
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
        addedMember.append(`<span>${member.name} <button type="button" onclick="removeMember('${member.email}')">x</button></span>`)
    })
}

function removeMember(email) {
    selectedMembers = selectedMembers.filter(member => member.email !== email)
    renderSelectedMembers()
    renderSearchResults()  
}


searchBTN.on("click", searchMember)
searchbox.on("keydown", handleKeydown)