const titleInput = document.getElementById("title");
const startDateInput = document.getElementById("start_date")
const endDateInput = document.getElementById("end_date")
const submitBtn = document.getElementById("submit-btn")
const searchBTN = document.getElementById("search-member")
const searchbox = document.getElementById("search-box")
const searchResult = document.getElementById("search-result")

//필수 입력 필드 다 채워졌는지 확인하고 버튼 상태 결정 (필수 입력: 프로젝트 타이틀, 기간)
function checkRequiredFields() {
const isTitleFilled = titleInput.value.trim() !== "";
const isStartDateFilled = startDateInput.value.trim() !== "";
const isEndDateFilled  = endDateInput.value.trim() !== "";

if (isTitleFilled && isStartDateFilled && isEndDateFilled) {
    submitBtn.disabled = false ;
} 
else { 
    submitBtn.disabled = true ;
}
} 
titleInput.addEventListener("input", checkRequiredFields)
startDateInput.addEventListener("input", checkRequiredFields)
endDateInput.addEventListener("input", checkRequiredFields)

checkRequiredFields();

//팀원 검색
function searchMember() {
    const searchValue = searchbox.value
    const url=`/api/users/search?search_member=${searchValue}`
    fetch(url).then(response => response.json()).then(data => {
        searchResult.innerHTML = ""
        data.forEach(user => {
         searchResult.innerHTML += `<div>${user.name} - ${user.email}</div>`   
         <button onclick="addMember(${user.name},${user.email}">
        })
    })

}
function handleKeydown(event) { 
    if (event.key == "Enter") {
        searchMember()
    }

}

searchBTN.addEventListener("click", searchMember)
searchbox.addEventListener("keydown", handleKeydown)