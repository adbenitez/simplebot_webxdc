HTML_FILE = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="webxdc.js"></script>
    <link rel="stylesheet" href="./styles.css">
  </head>
  <body>
   <div id="root"><div>
   <script src="./main.js"></script>
  </body>
</html>
"""

CSS_FILE = """
html {
    height: 100%;
    background-color: #4158D0;
    background-image: linear-gradient(43deg, #4158D0 0%, #C850C0 46%, #FFCC70 100%);
    background-attachment: fixed;
}

body {
   margin: 0;
   padding: 1em;
}

h3 {
    margin: 0;
}

em {
    color: #bfbfbf;
}

.card {
    border-radius: 1em;
    margin-left: auto;
    margin-right: auto;
    padding: 1em 1em 2em 1em;
    max-width: 50em;
    background: white;
    margin-bottom: 1em;
}

.card img {
    position: relative;
    border-radius: 1em;
    width: 30%;
    max-width: 8em;
    min-width: 4em;
    height: auto;
}

.flex {
    display: flex;
    flex: 1 1 0%;
    align-items: flex-start;
}

.flex-1 {
    flex: 1 1 0%;
    padding-left: 1em;
}

a {
    color: #3792fc;
    text-decoration: none;
}

a.btn {
    color: #fff;
    background: #3792fc;
    padding: 1em;
    border-radius: 1em;
}
"""

JS_FILE = """
function d(btn, appId) {
    btn.innerText = "Downloading...";
    btn.style.background = "#bfbfbf";
    btn.setAttribute("onclick", "");
    let cmd = "/download " + appId;
    window.webxdc.sendUpdate({payload: {simplebot: {text: cmd}}}, cmd);
}

function h(tag, attributes, ...children) {
    const element = document.createElement(tag);
    if (attributes) {
        Object.entries(attributes).forEach(entry => {
            element.setAttribute(entry[0], entry[1]);
        });
    }
    element.append(...children);
    return element;
}

function main(data) {
  let root = document.getElementById("root");
  data.forEach(meta => {
    root.appendChild(h("div", {class: "card"},
      h("div", {class: "flex"},
        h("img", {src: meta.icon}),
        h("div", {class: "flex-1"},
          h("h3", {}, meta.name),
          h("small", {},
            h("em", {}, "by ", meta.publisher, h("br"), meta.version)
          )
        )
      ),
      h("p", {}, meta.description),
      h("br"),
      h("a", {class: "btn", href: "#", onclick: "d(this, '" + meta.id + "'); return false;"}, "Download")
      ));
  });
}

onload = () => {
    fetch("data.json")
        .then(response => response.json())
        .then(json => main(json));
};
"""
