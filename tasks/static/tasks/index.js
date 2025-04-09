const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const completedBts = document.querySelectorAll('#completed-bt');
const unCompletedBts = document.querySelectorAll('#un-completed-bt');
const cancellBts = document.querySelectorAll('#cancell-bt')

async function patchTaskStatus(instanceId, taskStatus) {
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

async function checkTaskRecursion(instanceId) {
  const url = `/tasks/check_recursion/${instanceId}`
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  const data = await response.json();
  return data.is_recursive;
}

async function deleteTask(instanceId, removeFutureTask = false) {
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

if (completedBts) {
  completedBts.forEach(bt => {
    bt.addEventListener('click', async function (e) {
      e.preventDefault();
      const instanceId = this.getAttribute('data-instance-id');
      const instanceStatus = this.innerHTML.trim().toLowerCase()
      await patchTaskStatus(instanceId, instanceStatus);
    })
  })
}

if (unCompletedBts) {
  unCompletedBts.forEach(bt => {
    bt.addEventListener('click', async function (e) {
      e.preventDefault();
      const instanceId = this.getAttribute('data-instance-id');
      await patchTaskStatus(instanceId, 'pending');
    })
  })
}

// this should be delete method
if (cancellBts) {
  cancellBts.forEach(bt => {
    bt.addEventListener('click', async function (e) {
      e.preventDefault();
      const instanceId = this.getAttribute('data-instance-id');
      const isRecursive = await checkTaskRecursion(instanceId);
      if (isRecursive) {
        // if recursive task
        if (confirm("Do you want to remove all future tasks?")) {
          // remove all future tasks
          console.log("i will remove all of future tasks!")
          deleteTask(instanceId, true);
        }
      } else {
        // non-recursive
        // do request delete it directly
        deleteTask(instanceId, false);
      }
    })
  })
}
