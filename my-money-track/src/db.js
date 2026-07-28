const DB_NAME = 'MyMoneyTrackDB'
const DB_VERSION = 1
let db = null

export function initDB() {
  return new Promise((resolve, reject) => {
    try {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => {
        console.error('IndexedDB error:', request.error)
        reject(request.error)
      }

      request.onsuccess = () => {
        db = request.result
        resolve(db)
      }

      request.onupgradeneeded = (event) => {
        const database = event.target.result

        if (!database.objectStoreNames.contains('investimentos')) {
          const store = database.createObjectStore('investimentos', { keyPath: 'id', autoIncrement: true })
          store.createIndex('nome', 'nome', { unique: false })
          store.createIndex('tipo', 'tipo', { unique: false })
        }

        if (!database.objectStoreNames.contains('rendas')) {
          const store = database.createObjectStore('rendas', { keyPath: 'id', autoIncrement: true })
          store.createIndex('fonte', 'fonte', { unique: false })
        }

        if (!database.objectStoreNames.contains('despesas')) {
          const store = database.createObjectStore('despesas', { keyPath: 'id', autoIncrement: true })
          store.createIndex('categoria', 'categoria', { unique: false })
        }

        if (!database.objectStoreNames.contains('dividas')) {
          database.createObjectStore('dividas', { keyPath: 'id', autoIncrement: true })
        }

        if (!database.objectStoreNames.contains('config')) {
          database.createObjectStore('config', { keyPath: 'key' })
        }
      }
    } catch (error) {
      console.error('Failed to initialize IndexedDB:', error)
      reject(error)
    }
  })
}

function getStore(storeName, mode = 'readonly') {
  if (!db) throw new Error('Database not initialized')
  const tx = db.transaction(storeName, mode)
  return tx.objectStore(storeName)
}

export function addInvestimento(data) {
  return new Promise((resolve, reject) => {
    try {
      const store = getStore('investimentos', 'readwrite')
      const request = store.add({ ...data, createdAt: Date.now() })
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    } catch (error) {
      reject(error)
    }
  })
}

export function getInvestimentos() {
  return new Promise((resolve, reject) => {
    try {
      const store = getStore('investimentos')
      const request = store.getAll()
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    } catch (error) {
      reject(error)
    }
  })
}

export function deleteInvestimento(id) {
  return new Promise((resolve, reject) => {
    try {
      const store = getStore('investimentos', 'readwrite')
      const request = store.delete(id)
      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    } catch (error) {
      reject(error)
    }
  })
}

export function addRenda(data) {
  return new Promise((resolve, reject) => {
    try {
      const store = getStore('rendas', 'readwrite')
      const request = store.add({ ...data, createdAt: Date.now() })
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    } catch (error) {
      reject(error)
    }
  })
}

export function getRendas() {
  return new Promise((resolve, reject) => {
    try {
      const store = getStore('rendas')
      const request = store.getAll()
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    } catch (error) {
      reject(error)
    }
  })
}

export function addDespesa(data) {
  return new Promise((resolve, reject) => {
    try {
      const store = getStore('despesas', 'readwrite')
      const request = store.add({ ...data, createdAt: Date.now() })
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    } catch (error) {
      reject(error)
    }
  })
}

export function getDespesas() {
  return new Promise((resolve, reject) => {
    try {
      const store = getStore('despesas')
      const request = store.getAll()
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    } catch (error) {
      reject(error)
    }
  })
}

export function getConfig(key) {
  return new Promise((resolve, reject) => {
    try {
      const store = getStore('config')
      const request = store.get(key)
      request.onsuccess = () => resolve(request.result?.value)
      request.onerror = () => reject(request.error)
    } catch (error) {
      reject(error)
    }
  })
}

export function setConfig(key, value) {
  return new Promise((resolve, reject) => {
    try {
      const store = getStore('config', 'readwrite')
      const request = store.put({ key, value })
      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    } catch (error) {
      reject(error)
    }
  })
}

export function clearAllData() {
  return new Promise((resolve, reject) => {
    try {
      const stores = ['investimentos', 'rendas', 'despesas', 'dividas']
      let completed = 0
      stores.forEach(storeName => {
        const store = getStore(storeName, 'readwrite')
        const request = store.clear()
        request.onsuccess = () => {
          completed++
          if (completed === stores.length) resolve()
        }
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      reject(error)
    }
  })
}

export function exportData() {
  return new Promise(async (resolve, reject) => {
    try {
      const data = {
        investimentos: await getInvestimentos(),
        rendas: await getRendas(),
        despesas: await getDespesas(),
        exportDate: new Date().toISOString()
      }
      resolve(data)
    } catch (error) {
      reject(error)
    }
  })
}
