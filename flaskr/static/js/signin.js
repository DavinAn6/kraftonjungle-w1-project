var isEmail = "";
var isUsername = "";
var isPassword = "";
/** TODO: ajax로 사용가능한 이메일인지 검증**/
function chkEmail() {
    var email = $("#email").val();
    var regexp = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    if (!regexp.test(email)) {
        $("#useEmail").text("❌올바른 이메일 주소가 아닙니다.");
        $("#email").focus();
        isEmail = "";
        return;
    }

    $.ajax({
        url: "/signin/check/email",
        type: "post",
        data: { "email": email },
        success: function (data, status, xhr) {
            if (data) {
                $("#useEmail").text("✅사용가능한 이메일 입니다.");
                isEmail = email;
            }
            else {
                $("#useEmail").text("❌중복된 이메일 입니다.");
                isEmail = "";
            }
        }
    })
    return;
}
/** TODO: ajax로 사용가능한 ID인지 검증**/
function chkID() {
    var username = $("#username").val();
    var regexp = /^[a-zA-Z0-9_-]{8,50}$/
    if (!regexp.test(username)) {
        $("#useUsername").text("❌아이디는 8자 이상 알파벳 소문자, 대문자, 숫자, 하이픈을 사용해주세요.");
        $("#username").focus();
        isUsername = "";
        return;
    }

    $.ajax({
        url: "/signin/check/username",
        type: "post",
        data: { "username": username },
        success: function (data, status, xhr) {
            if (data) {
                $("#useUsername").text("✅사용가능한 아이디입니다.");
                isUsername = username;
            }
            else {
                $("#useUsername").text("❌중복된 아이디입니다.");
                isUsername = "";
            }
        }
    })
    return;
}

function chkPassword() {
    var ori_password = $("#password").val();
    var rep_password = $("#chkpassword").val();

    if (ori_password !== rep_password) {
        $("#usePasswd").text("❌비밀번호가 다릅니다.");
        isPassword = "";
        return
    }
    $("#usePasswd").text("✅");
    isPassword = ori_password;
    return;
}

$("#signin_form").on("submit", function (event) {
    var isValidEmail = isEmail === $("#email").val();
    var isValidUsername = isUsername === $("#username").val();
    var isValidPassword = isPassword === $("#password").val();

    if (!(isValidEmail && isValidUsername && isValidPassword)) {
        event.preventDefault();
        alert("항목을 다시 점검해 주세요");
        return;
    }
})