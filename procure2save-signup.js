// Paste only the public iframe URL from Brevo's confirmed subscription form.
const procure2saveFormUrl = "";

function showProcure2saveSignup(container, compact) {
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = compact ? "Subscribe to Procure2save by email" : "Procure2save — Insights delivered to your inbox.";
  details.append(summary);
  const intro = document.createElement("p");
  intro.textContent = "Subscribe to receive my latest articles exploring public procurement, commercial law, public policy, government contracting and governance.";
  const frequency = document.createElement("p");
  frequency.textContent = "No daily updates. No unnecessary emails. Just thoughtful professional analysis whenever a new article is published.";
  const privacy = document.createElement("p");
  privacy.innerHTML = 'Brevo processes your email address and confirmation to deliver Procure2save and report delivery, opens and clicks. Confirm by email to subscribe. Every edition includes an unsubscribe link. For access, export or deletion, <a href="mailto:kaycee_god@yahoo.com">contact Kelechi</a>. <a href="https://www.brevo.com/legal/privacypolicy/">Brevo privacy policy</a>.';
  details.append(intro, frequency, privacy);
  if (procure2saveFormUrl) {
    const frame = document.createElement("iframe");
    frame.title = "Confirm your Procure2save email subscription";
    frame.src = procure2saveFormUrl;
    frame.loading = "lazy";
    frame.style.cssText = "width:100%;height:28rem;border:0;background:white";
    const link = document.createElement("a");
    link.href = procure2saveFormUrl;
    link.textContent = "Open the subscription form directly";
    details.append(frame, link);
  } else {
    const status = document.createElement("p");
    status.textContent = "Email subscriptions will open soon.";
    details.append(status);
  }
  details.open = !compact;
  details.style.cssText = "max-width:42rem;min-width:0;text-align:left;line-height:1.5;font-size:1rem;margin-block:1rem";
  summary.style.cssText = "cursor:pointer;font-weight:700";
  container.append(details);
}
document.querySelectorAll("[data-procure2save-signup]").forEach(el => showProcure2saveSignup(el, false));
document.querySelectorAll("body footer").forEach(el => showProcure2saveSignup(el, true));
