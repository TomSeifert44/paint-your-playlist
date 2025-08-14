  /* script for showing hidden items with "see more" button */

  const seeMoreBtn = document.getElementById('seeMoreBtn');

  /* capture all elements with class .hidden-item (querySelectorAll docs 31 May 2025) */
  const hiddenItems = document.querySelectorAll('.hidden-item');

  /* define variable expanded (let docs 31 May 2025) */
  let expanded = false;

  /* bind button to function (addEventListener docs 31 May 2025) */ 
  seeMoreBtn.addEventListener('click', () => {
    if (!expanded) {
      /* if expanded, show hidden items (querySelectorAll docs 31 May 2025) */
      hiddenItems.forEach(item => item.style.display = 'list-item');
      /* change button text to "See Less" */
      seeMoreBtn.textContent = 'See Less';
    } else {
      /* if not expanded, hide hidden items (querySelectorAll docs 31 May 2025) */
      hiddenItems.forEach(item => item.style.display = 'none');
      /* change button text to "See More" */
      seeMoreBtn.textContent = 'See More';
    }
    /* toggle expanded variable */
    expanded = !expanded;
  });