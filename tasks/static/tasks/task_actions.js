const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
// NOTE:
// Deal with those errors, it should not be see in frontend

export async function patchTaskStatus(instanceId, taskStatus) {
    const url = `/tasks/${instanceId}`
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
    const url = `/tasks/${instanceId}`
    const response = await fetch(url);
  
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    console.log(data);
    return data.recursion_rule;
  }
  
  export async function deleteTask(instanceId, removeFutureTask = false) {
    let url = `/tasks/${instanceId}`;
    let body = { 'delete_future_tasks': removeFutureTask };
  
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