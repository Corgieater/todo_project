const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

export async function patchTaskStatus(instanceId, taskStatus) {
    const url = `/tasks/update/${instanceId}`
    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        status: taskStatus,
      })
    });
  
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
  
    window.location.reload();
  }
  
  export async function checkTaskRecursion(instanceId) {
    const url = `/tasks/check_recursion/${instanceId}`
    const response = await fetch(url);
  
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    return data.is_recursive;
  }
  
  export async function deleteTask(instanceId, removeFutureTask = false) {
    let url = `/tasks/delete/${instanceId}`;
    let body = { 'delete_future_tasks': false };
  
    if (removeFutureTask) {
      body['delete_future_tasks'] = true;
    }
  
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ body })
    });
  
    if (response.ok) {
      window.location.reload();
    }
  }