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
  // console.log(evt.data)
  let obj = JSON.parse(evt.data)
  if (obj.value) {
    plog(obj.value, obj.type)
  }

  switch (obj.type) {
    case 'success':
      announce('success', obj.value)
      enableButton('button.next', true)
      break
    case 'error':
      announce('failure', obj.value)
      enableButton('button.show-errors', true)
      $('.modal-body pre').text(obj.stacktrace)
      break
    case 'stop':
    case 'finish':
      enableButton('button.start', true)
      enableButton('button.stop', false)
      if (obj.type === 'stop') {
        plog('Command was stopped by user', 'highlight')
      }
      break
    default:
      break
  }
}

$('button.start').on('click', () => {
  $.get('start/', (data) => {
    if (data === 'ok') {
      enableButton('button.start', false)
      enableButton('button.stop', true)
    }
  })
})

$('button.stop').on('click', () => {
  $.get('stop/')
  plog('Stopping command...')
})


$('button.next').on('click', function(evt) {
  document.location = $(this).data('url')
})


function enableButton(selector, enabled) {
  let btn = $(selector)
  if (enabled) {
    btn.removeClass('disabled')
    btn[0].disabled = false
  } else {
    btn.addClass('disabled')
    btn[0].disabled = true
  }
}


function plog(text, cls) {
  let output = $('.console')
  let p = $('<p>').text(text)  
  p.html(p.html().replace(/\n/g, '<br>'))
  p.appendTo(output)
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

  return new Promise((resolve, reject) => {
    let utterance = new SpeechSynthesisUtterance(text)
    window.speechSynthesis.speak(utterance)
    utterance.onend = resolve
  })
}


let sfx = jsfx.Sounds(window.soundEffectsLibrary)

function playSound(name) {
  return new Promise((resolve, reject) => {
    sfx[name]()
    window.setTimeout(resolve, 1000)
  })
}


function announce(sound, text) {
  playSound(sound).then(() => speak(text))
}
