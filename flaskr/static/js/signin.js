let verifiedEmail = "";
let verifiedUsername = "";

const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
const usernamePattern = /^[a-zA-Z0-9_-]{8,50}$/;

function chkEmail() {
    const $email = $("#email");
    const email = $email.val().trim();

    if (!emailPattern.test(email)) {
        $("#useEmail").text("❌ 올바른 이메일 주소가 아닙니다.");
        $email.focus();
        return;
    }

    $.post("/signin/check/email", { email })
        .done(function (available) {
            if (available) {
                $email.val(email);
                verifiedEmail = email;
                $("#useEmail").text("✅ 사용할 수 있는 이메일입니다.");
                return;
            }
            $("#useEmail").text("❌ 이미 사용 중인 이메일입니다.");
        })
        .fail(function () {
            $("#useEmail").text("❌ 중복 확인에 실패했습니다.");
        });
}

function chkID() {
    const $username = $("#username");
    const username = $username.val().trim();

    if (!usernamePattern.test(username)) {
        $("#useUsername").text("❌ 영문, 숫자, 밑줄, 하이픈을 사용해 8자 이상 입력하세요.");
        $username.focus();
        return;
    }

    $.post("/signin/check/username", { username })
        .done(function (available) {
            if (available) {
                $username.val(username);
                verifiedUsername = username;
                $("#useUsername").text("✅ 사용할 수 있는 아이디입니다.");
                return;
            }
            $("#useUsername").text("❌ 이미 사용 중인 아이디입니다.");
        })
        .fail(function () {
            $("#useUsername").text("❌ 중복 확인에 실패했습니다.");
        });
}

function chkPassword() {
    const password = $("#password").val();
    const confirmation = $("#chkpassword").val();

    if (!confirmation) {
        $("#usePasswd").text("");
        return false;
    }
    if (password.length < 8 || password !== confirmation) {
        $("#usePasswd").text("❌ 비밀번호가 일치하지 않습니다.");
        return false;
    }
    $("#usePasswd").text("✅ 비밀번호가 일치합니다.");
    return true;
}

$("#checkEmailBtn").on("click", chkEmail);
$("#checkUsernameBtn").on("click", chkID);
$("#password, #chkpassword").on("input", chkPassword);

$("#email").on("input", function () {
    verifiedEmail = "";
    $("#useEmail").text("");
});

$("#username").on("input", function () {
    verifiedUsername = "";
    $("#useUsername").text("");
});

$("#signin_form").on("submit", function (event) {
    const emailIsVerified = verifiedEmail === $("#email").val().trim();
    const usernameIsVerified = verifiedUsername === $("#username").val().trim();

    if (!emailIsVerified || !usernameIsVerified || !chkPassword()) {
        event.preventDefault();
        alert("입력 항목과 중복 확인 결과를 다시 확인해주세요.");
    }
});
