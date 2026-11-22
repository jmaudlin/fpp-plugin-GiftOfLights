<div class="container-fluid px-0" id="golPage">
  <h2 class="h4">Gift of Lights: now playing</h2>
  <p class="text-body-secondary">
    Sends the song that is playing (title and artist from the song's tags) and the show (the playlist's name) to the
    Gift of Lights page on the website, as each song starts. It sends nothing while the switch below is off.
  </p>

  <div class="border rounded p-3 mb-3">
    <div class="form-check form-switch mb-3">
      <input class="form-check-input" type="checkbox" role="switch" id="golEnabled">
      <label class="form-check-label" for="golEnabled">Send now playing to the website</label>
    </div>

    <label class="form-label" for="golUrl">Website address</label>
    <input class="form-control mb-1" type="url" id="golUrl" placeholder="https://mahaskadrug-photos.azurewebsites.net/api/lightshow/now-playing" autocomplete="off">
    <div class="form-text mb-3">The website's now-playing address, starting https://.</div>

    <label class="form-label" for="golKey">Key</label>
    <input class="form-control mb-1" type="password" id="golKey" autocomplete="new-password" placeholder="Leave blank to keep the saved key">
    <div class="form-text mb-3" id="golKeyNote">The same value as the website's LIGHTSHOW_FEED_KEY setting.</div>

    <label class="form-label" for="golNames">Show names (optional)</label>
    <textarea class="form-control mb-1" id="golNames" rows="4" placeholder="Show 1 = The Toy Shop&#10;Ambient = Between shows"></textarea>
    <div class="form-text mb-3">One per line: <code>playlist name = name on the website</code>. A playlist not listed shows under its own name.</div>

    <div class="d-flex flex-wrap gap-2">
      <button type="button" class="buttons btn btn-success" id="golSave">Save</button>
      <button type="button" class="buttons btn btn-outline-secondary" id="golTest">Send a test song</button>
    </div>
  </div>

  <div class="border rounded p-3">
    <h3 class="h6">Status</h3>
    <dl class="row mb-0" id="golStatus">
      <dt class="col-sm-3">Sender</dt><dd class="col-sm-9" id="golRunning">-</dd>
      <dt class="col-sm-3">Last sent</dt><dd class="col-sm-9" id="golLast">-</dd>
      <dt class="col-sm-3">Last problem</dt><dd class="col-sm-9" id="golError">-</dd>
      <dt class="col-sm-3">Waiting</dt><dd class="col-sm-9" id="golWaiting">-</dd>
    </dl>
  </div>
</div>
