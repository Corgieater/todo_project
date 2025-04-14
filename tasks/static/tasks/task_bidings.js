import { patchTaskStatus, checkTaskRecursion, deleteTask } from './task_actions.js'

const completedBts = document.querySelectorAll('#completed-bt');
const unCompletedBts = document.querySelectorAll('#un-completed-bt');
const cancellBts = document.querySelectorAll('#cancell-bt');
const editBts = document.querySelectorAll('#edit-bt');


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

// do Edit bts
if (editBts) {
  editBts.forEach(bt => {
    bt.addEventListener('click', async function (e) {
      e.preventDefault();
      const instanceId = this.getAttribute('data-instance-id');
      console.log('edit this', instanceId);
      
      // await patchTaskStatus(instanceId, 'pending');
    })
  })
}