# TODO List for Event Promotion and Interactive Calendar Features

## 1. Facebook Promotion Feature
- [x] Add Facebook API credentials to settings.py
- [x] Install Facebook SDK (facebook-sdk or similar)
- [x] Update Evenement model to include Facebook page ID field
- [x] Create a promote_event function in views.py to handle posting to Facebook
- [x] Add promote URL to urls.py
- [x] Update admin_interface.html to include promote button for each event
- [x] Implement logic to create Facebook page if it doesn't exist

## 2. Interactive Calendar for Non-Admin Users
- [x] Install FullCalendar or similar JavaScript library
- [x] Create a calendar view in views.py that filters events by closest dates
- [x] Add calendar URL to urls.py
- [x] Create calendar.html template with interactive calendar
- [x] Implement AJAX or modal for event details on click
- [x] Update navigation to include calendar link for non-admin users

## 3. Testing and Refinement
- [ ] Test Facebook posting functionality
- [ ] Test calendar display and interaction
- [ ] Ensure admin-only access for promotion
- [ ] Handle errors gracefully (e.g., API failures)
