const completedBts = document.querySelectorAll('#completed-bt');

async function patchTaskStatus(instanceId, status){
    const url = `/tasks/update/${instanceId}`
    console.log(url)
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const response = await fetch(url, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          status: status,
        })
      });
    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

    window.location.reload();

}
if (completedBts){
  completedBts.forEach(bt => {bt.addEventListener('click', async function(e){
        e.preventDefault();
        const instanceId = this.getAttribute('data-instance-id');
        const instanceStatus = this.innerHTML.trim().toLowerCase()
        await patchTaskStatus(instanceId, instanceStatus);
    })})
}
