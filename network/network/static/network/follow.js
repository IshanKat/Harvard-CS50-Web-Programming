follow_btn = document.querySelector("#follow-btn");
follow_btn.addEventListener("click", () => {
  user = follow_btn.getAttribute("data-user");
  action = follow_btn.textContent.trim();
  form = new FormData();
  form.append("user", user);
  form.append("action", action);
  fetch("/follow/", {
    method: "POST",
    body: form,
  })
    .then((result) => result.json())
    .then((result) => {
      if (result.status == 201) {
        follow_btn.textContent = result.action;
        document.querySelector(
          "#follower"
        ).textContent = `Followers ${result.follower_count}`;
      }
    });
});
