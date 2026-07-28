const listeners = {}

export function on(event, fn) {
  if (!listeners[event]) listeners[event] = []
  listeners[event].push(fn)
  return () => { listeners[event] = listeners[event].filter(f => f !== fn) }
}

export function emit(event, data) {
  if (!listeners[event]) return
  listeners[event].forEach(fn => {
    try { fn(data) } catch (e) { console.warn(`event-bus[${event}]:`, e) }
  })
}

export function clear(event) {
  if (event) delete listeners[event]
  else Object.keys(listeners).forEach(k => delete listeners[k])
}
