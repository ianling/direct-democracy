This is a small proof of concept electronic voting system. This system aims to solve three main problems with traditional voting methods:

* Inability to verify that votes were counted accurately, or that your vote was counted at all
* Accessibility, inconvenience
* Inefficiency

In order to vote using this system, one has to verify their identity by entering their personal details (name and SSN), as well as their unique one-time use code. For the purpose of this demonstration, you can assume that this code is physically mailed to them on a small postcard.

After they have verified their identity, they will be able to vote in any active polls that they have not already voted in.

Once they have submitted a vote in a poll, the vote is assigned a unique ID that is not derived from their identity. In other words, if you are shown a vote and its unique ID, you will not be able to determine who cast that vote.

When the poll has closed and all votes have been collected, a spreadsheet containing each vote and their unique IDs will be released to the public. This will allow people to quickly tally all the votes themselves, and verify that their unique vote ID is contained within the file.

The SHA256 hash of the results file will be published as well, allowing people to verify that everyone is looking at the exact same set of results and no file tampering is occurring on an individual basis.

This spreadsheet could be expanded to contain non-identifying information about the voters that could be valuable for statisticians, such as their region, age group, household income, etc.

## Requirements
* Python 3
* Flask

## Demo limitations
This POC has several intentional limitations in its implementation in order to better demonstrate the system.

* All users are authenticated as the same identity in the backend, and one-time use codes do not expire. This is to avoid dealing with the one-time use codes for this demo.
* The browser session is used to keep track of which polls a user has voted in, rather than using the database. This means that if you vote in a poll, you can simply clear your cookies in order to vote again. This is to allow users to test the system more thoroughly.

## Security considerations
As with any system containing sensitive data, there are a number of things to be considered when securing this application.

* Encrypting data in transit (e.g. HTTPS)
* CSRF
* XSS on write-ins
* Hardening the servers hosting the application and database
* Administrators having access to the application source code and database

## Practical considerations
* Supplying all citizens with one-time use codes every election cycle
  * Could use something similar to Oregon's existing vote-by-mail system to mail a code to each person
  * Could use an app, email, or other electronic means to supply the code
  
## Contributing
If you can think of a logical issue, potential security hole, or a practical constraint that you believe this system fails to address, open an issue for community discussion.

If you want to improve the demo's code in any way, create a pull request.