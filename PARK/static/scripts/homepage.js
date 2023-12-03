// hourly and monthly buttons that change search parameters
document.addEventListener('DOMContentLoaded', (event) => {
    const hourlyBtn = document.getElementsByClassName('hourly')[0];
    const monthlyBtn = document.getElementsByClassName('monthly')[0];
  
    hourlyBtn.addEventListener('click', function() {
      hourlyBtn.classList.add('active');
      monthlyBtn.classList.remove('active');
    });
  
    monthlyBtn.addEventListener('click', function() {
      monthlyBtn.classList.add('active');
      hourlyBtn.classList.remove('active');

    });
  });

  // hourly and monthly buttons that change search parameters
document.addEventListener('DOMContentLoaded', (event) => {
    const hourlyBtn = document.getElementsByClassName('hourly')[0];
    const monthlyBtn = document.getElementsByClassName('monthly')[0];
    const startTime = document.getElementById('start-time');
    const endTime = document.getElementById('end-time');
  
    hourlyBtn.addEventListener('click', function() {
      hourlyBtn.classList.add('active');
      monthlyBtn.classList.remove('active');
      startTime.style.display = 'inline-block';
      endTime.style.display = 'inline-block';
    });
  
    monthlyBtn.addEventListener('click', function() {
      monthlyBtn.classList.add('active');
      hourlyBtn.classList.remove('active');
      startTime.style.display = 'none';
      endTime.style.display = 'none';
    });
  });
  
