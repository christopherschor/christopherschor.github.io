// Keep comparisons clear: only one cue plays at a time.
document.addEventListener('play', (event) => {
  if (!(event.target instanceof HTMLAudioElement)) return;
  document.querySelectorAll('audio').forEach((player) => {
    if (player !== event.target) player.pause();
  });
}, true);
