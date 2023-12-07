# playing-with-intervals #

### Table of contents ###
* [What is this repository for?](#what-is-this-repository-for)
* [How do I get set up?](#how-do-i-get-set-up)
* [Who do I talk to?](#who-do-i-talk-to)

### What is this repository for? ###

This is a fun little programming exercise I challenged myself with a short time ago. The intent is to figure out whether a status applies to a dataset. The four statuses correspond to Gretchen Rubin's Four Tendencies, but can obviously be applied to any real-world model.

In this scenario, a person can have one or more records that specify his or her status, effective in the supplied date range (or if not, applicable always). If I supply those records and a reporting date range to the function, I want to find if a person is in the status I'm looking for.

As an example:
* I know a person is in the `UPHOLDER` status from `2018-05-01` to `2018-05-04`, but only from `8am` to `12pm`.
* I know that person is in the `OBLIGER` status on `2018-05-03` for the whole day.
* I want to know if the `UPHOLDER` status applies on `2018-05-03` at `9am`, so I supply the target status, the date range, and the above records to the function. The result is `UPHOLDER` because the person had that status at that time.
* I want to know if the `OBLIGER` status applies on `2018-05-04` at `9am`, so I supply the target status, the date range, and the above records to the function. The result is `0` because the person did not have that status at that time.

I've immortalized it here as a reference. Feel free to pick it apart ;)

### How do I get set up? ###

* What you need
    1. [Python](https://www.python.org/downloads) v2.7.x (or later, but I haven't tested 3+).
* What you do
    1. Run the script! It's that easy.
