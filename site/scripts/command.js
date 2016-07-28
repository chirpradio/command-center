'use strict';

let loc = document.location
let url = 'ws://' + loc.host + loc.pathname + 'messages/'
let ws = new WebSocket(url)

ws.onopen = () => {
  console.log('Websocket opened');
}

ws.onclose = () => {
  console.log('Websocket closed');
}

ws.onmessage = (evt) => {
  let obj = JSON.parse(evt.data)
  plog(obj.value, obj.type)
  if (obj.type == 'success') {
    speak(obj.value)
  }
}

$('button.start').on('click', () => {
  $.get('start/', (data) => {
    console.log(data)
  })
})

$('button.stop').on('click', () => {
  $.get('stop/', (data) => {
    console.log(data)
  })
})


function plog(text, cls) {
  let output = $('.console')
  let p = $('<p>').text(text).appendTo(output)
  if (cls) {
    p.addClass(cls)
  }
  // Make output scroll to the bottom.
  output.scrollTop(p.offset().top - output.offset().top + output.scrollTop())
}


function speak(text) {
  if (window.speechSynthesis === undefined) {
    return Promise.resolve()
  }

  return new Promise(function(resolve, reject) {
    let utterance = new SpeechSynthesisUtterance(text)
    window.speechSynthesis.speak(utterance)
    utterance.onend = resolve
  })
}
