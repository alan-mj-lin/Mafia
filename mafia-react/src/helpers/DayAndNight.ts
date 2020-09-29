export function styleNight(): void {
  document.body.setAttribute('data-is-night', 'true');
}

export function styleDay(): void {
  document.body.setAttribute('data-is-night', 'false');
}
