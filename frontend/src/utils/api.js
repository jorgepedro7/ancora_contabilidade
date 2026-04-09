export function extractApiErrorMessage(error, fallback = 'Ocorreu um erro.') {
  const responseData = error?.response?.data

  if (!responseData) {
    return error?.message || fallback
  }

  if (typeof responseData === 'string') {
    return responseData
  }

  if (Array.isArray(responseData.errors) && responseData.errors.length > 0) {
    const details = responseData.errors
      .map((item) => item?.field ? `${item.field}: ${item.message}` : item?.message)
      .filter(Boolean)
      .join(' | ')

    if (details) {
      return responseData.message ? `${responseData.message} ${details}` : details
    }
  }

  if (typeof responseData.message === 'string' && responseData.message.trim()) {
    return responseData.message
  }

  return fallback
}
