/**
  * From: https://codeburst.io/throttling-and-debouncing-in-javascript-b01cad5c8edf
*/
const throttle = (func, limit) => {
  let lastFunc
  let lastRan
  return function() {
    const context = this
    const args = arguments
    if (!lastRan) {
      func.apply(context, args)
      lastRan = Date.now()
    } else {
      clearTimeout(lastFunc)
      lastFunc = setTimeout(function() {
        if ((Date.now() - lastRan) >= limit) {
          func.apply(context, args)
          lastRan = Date.now()
        }
      }, limit - (Date.now() - lastRan))
    }
  }
}

// These events are used to check if the user is active or AFK
// They are throttled to prevent huge number of pycmd calls

document.body.addEventListener('click', throttle(function() {
  return pycmd('click')
}, 1000));

document.body.addEventListener('keydown', throttle(function() {
  return pycmd('keydown')
}, 1000));

document.body.addEventListener('mousemove', throttle(function() {
  return pycmd('mousemove')
}, 1000));

document.body.addEventListener('click', throttle(function() {
    return pycmd('click')
}), 1000);

document.body.addEventListener('scroll', throttle(function() {
    return pycmd('scroll')
}), 1000);
