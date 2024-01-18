let respcon = document.getElementById("response-container");
function display(s, className = "") {
  let span = document.createElement("span");
  span.textContent = s;
  respcon.appendChild(span);
  if (className) {
    span.classList.add(className);
  }

  respcon.appendChild(span);
}

async function fetchPOST(endpoint, data) {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return response.text();
}

async function listen() {
  // listen until the end of the command buffer
  let data = {
    args: [],
  };
  if (await bufferIsEmpty()) {
    return ""; //nothing to listen for
  }
  let response = await fetchPOST("/pman/listen", data);
  while (!(await bufferIsEmpty())) {
    response = await fetchPOST("/pman/listen", data);
  }
  return response;
}

async function push(args) {
  const data = { args: args };
  return fetchPOST("/pman/push", data);
}

async function pull(args) {
  const data = { args: args };
  return fetchPOST("/pman/pull", data);
}

async function bufferIsEmpty() {
  return parseInt(await fetchPOST("/pman/buffer-is-empty"));
}

const example_data = { args: [0, 1, 120] };
