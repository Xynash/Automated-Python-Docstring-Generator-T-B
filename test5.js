async function syncUserData(userId) {
  const response = await fetch(`/api/users/${userId}/sync`);
  const result = await response.json();
  return result.status === 'success';
}