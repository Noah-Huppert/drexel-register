 Drexel Register
A helper program for Drexel course registration.

Here is the process:
- User declares which courses they have to take
    - Mandatory
        - Subject Code
        - Course No.
    - Optionally
        - Instruction types
            - Array of Section Instruction Types which make up the course
            - If not included program will try to figure it out
        - CRNs
            - Priority list per Instruction Type
- Program gathers data
    - Course info
        - Given in Configuration
            - Academic Year
            - Quarter
        - Located: On page of any section in course
            - Subject Code
            - Course No.
            - Course Title
            - Credits
            - College
            - Restrictions
            - Co-Requisites
            - Pre-Requisites
    - Section info
        - Located: Course search results page
            - Subject Code
            - Course No.
            - Instruction Type
            - Section
            - CRN
            - Days
            - Times
            - Instructor
        - Located: Section page
            - Credits
            - Campus
            - Instruction Method
            - Max Enroll
            - Enroll
            - Section comments
            - Textbooks
            - Start Date
            - End Date
            - Building
            - Room
- Ask user to rank each section for each course
    - Provide filtering options
    - User can mark classes as not an option as well
- Compute schedule with highest rank option for each course
- Let user tweak schedule
    - Allow user to choose specific course sections
- Compute 2 backups for each choice
- Generate final report
    - Overall schedule
    - Section for each Course
        - Backup sections + other changes needed to use backup choice
        - Restrictions if present
        - Pre-Requisites if present
        - Instruction Type
        - Days / Times
        - Section comments if present
    
# Algorithm
This section describes the entire process this program goes through to schedule.

It is here for those interested, I used this section to plan the program out so it is a bit informal.

## Gather Information
- User declares Courses in `config.yaml`
- Use Drexel Course Catalog site to find Courses title
    - Loop: For each Course
    - Url: `http://catalog.drexel.edu/search/?P=`**`<COURSE CODE>`**
    - Replace **`<COURSE CODE>`** with Course Subject Code plus Course Number, separated by a space
        - Ex., `CI 103` or `CS 172`
        - This will be referred to as the Course Code from now on.
    - Parse search results page:
        - Loop over `.courseblock`s
            - Find one where `.courseblocktitle > strong > span:nth-child(1)` is the Course Code
            - Extract:
                - Course Title
                - Credits
                - College
                - Co-Requisites
                - Pre-Requisites
            - Store as a "Course" in the "Courses" collection
                - Primary key: Course Code
                    - Subject Code + Course Number separated by a dash
- Scrape any courses found in the Co-Requisites section using the same procedure as above
- Use TMS Search page to navigate to Sections list for each Course
    - Loop: For each Course
    - Url: `https://duapp2.drexel.edu/webtms_du/app?page=Home&service=page`
    - Select correct term with config quarter and year
    - Enter Course Title into "Course Names and Keywords" text box
    - Click "Search Courses" button
    - Scrape the search results page
        - Loop over `<tr>`s
            - If Subject Code and Course Number match scrape row
            - Extract:
                - Course Code
                    - Comprised of:
                        - Subject Code
                        - Course No.
                - Instruction Type
                - Instruction Method
                - Section
                - CRN
                - Days
                - Times
                - Instructor
             - Store as "Section" in "Sections" collection
                - Primary key: CRN
                - Foreign Key: "Course".Course Code
- Scrape TMS Course Section pages
    - Loop: For each row of the Course search page
    - Url: Follow Url in CRN column
    - Extract **Once per Course**
        - The Restrictions field for a Course only shows up on a Course Section details page
        - This field only needs to be scraped off of one of the Sections details page per Course
        - Update "Course" item in "Courses" collection with scraped Restrictions value
    - Extract:
        - Credits
        - Campus
        - Max Enroll
        - Enroll
        - Section comments
        - Textbooks
        - Start Date
        - End Date
        - Building
        - Room
    - Update "Section" in "Sections" collection
## Schedule
In order to create the optimal schedule this program allows the user to enter restrictions and 
preferences in a variety of ways (Described later in this section). All these inputs end up defining a 
"Preference". 

The Preference model has the following fields:

- CRN
    - CRN of Course Section that preference relates to
- Instruction Type
    - Instruction Type of Course Section that preferences relates to
- Preference
    - Integer value in the range [-1, 101]
    - If value is in the range [1, 100]
        - Value represents user's preference about Section on the scale 1-100
        - 1 being the least preferred
        - 100 being the most preferred
    - If value is 0
        - The user has no preference about Section
        - This is useful in the scheduling algorithm to find sections to move around that don't 
          impact the user
    - If value is -1
        - This section is not an option
    - If value is 101
        - This section is required
        
Action:
- Parse Courses in `config.yaml` for an create Preferences, store in "Preferences" collection
- Present user with all Sections for each Course broken down by Instruction Type
- Get users preferences for each Course Section
    - Group Sections by Instruction Type
        - Ex., Present all the Lab Sections for ordering at the same time, then all the Lectures, and so on.
   - Store preferences as they are entered
   - Interface
    - List title will be "<Course Code> - <Instruction Type>s"
    - List with columns:
        - Preference value
        - CRN
        - Instruction Method
        - "<Enroll> / <Max Enroll>"
            - Overall column called "capacity" for queries
        - Days
        - Times
        - Instructor
    - Default state is to have cursor in list
        - User moves cursor up and down with arrow keys or j&k
        - A box will show user which keys they can press
            - a
                - Assign preference from 1-100
                - Hit enter to finalize
                - Hit esc to cancel
            - r 
                - Mark as required
                - Only 1 Section per Instruction Type can be marked as required
                - So if a Section is already marked, it will be unmarked
                - Toggles value
            - x
                - Mark as not an option
                - Toggles value
    - User can enter query mode at any time
        - By pressing q
        - Exit by pressing esc
        - User input is given to query box
        - While user is typing highlight list
        - Hit enter to filter displayed to just matching query (Or permanently highlight or something)
            - All keys that work in default state will now apply to entire list
            - a and r only work if entire list is 1 long
        - Query box expects Query Statements join by Logical Symbols (&& and ||)
            - Query Statement
                - In the format of `<key name> <comparor> <value>`
                    - `<key name>`
                        - Key in Section to check against
                        - This value is downcased for easier matching
                        - Accepts the following formats of keys:
                            - first second
                            - firstsecond
                            - first_second
                        - Program will assume the user only knows Section model keys via 
                          list columns on screen, so it will match against those names
                    - `<comparor>`
                        - Comparision to make
                        - Accepts the following comparors:
                            - `about`, `about equal`, `about equal to`, `~`, `~=`
                                - Uses fuzzy matching where it can
                            - `equal`, `equal to`, `=`, `==`
                            - `not equal`, `not equal to`, `!=`
                            - `greater`, `greater than`, `>`
                            - `greater or equal`, `greater than or equal to`, `>=`
                            - `less`, `less than`, `<`
                            - `less or equal`, `less than or equal to`, `<=`
                    - `<value>`
                        - Value to test against
                        - Cast into appropriate value based on `<key name>`
             - Logical Symbol
                - Used to combine Query Statements to create slightly more detailed queries
                 - Either:
                    - `and`, `&&` - And
                    - `or`, `||` - Or
                        - Chaining more than two Ors: This query system doesn't have to be too 
                          complicated so it views multiple statements as such:
                            - `(Query Statement 1) <logical symbol> (Query Statement 2) <logical symbol> (Query Statement 3)`
                            - So `(QS1) && (QS2) || (QS3)` would mean `QS1` has to be true AND `QS2` has to be true but `QS3` is optional
- Present user with all non manually specified as mandatory Instruction Types for each Course
    - Ask user to rank Course Instruction Type by preference
- Create base schedule object
    - Add all sections that are required
    - Add all sections that are the only option
    - Notify user of any conflicts on base schedule as there is nothing this program can do to fix those
- Starting with the highest preferred Course Instruction Type schedule the specific Sections
    - Start with base schedule object (This can't change ever)
    - If there is a conflict choose the lesser preferred Course Instruction Type and reschedule the 
      Course's Section the the one 1 less preferred.
    - If the one 1 less preferred creates a conflict apply the same logic
    - Whenever a Section moves (aka a slot of time becomes free) recheck all more preferred Sections 
      of all other Courses that got bumped to see if they can be fit back in
- For each Course Instruction Type attempt to create 2 backup schedules
    - Work off ideal schedule as base schedule (To reduce overall change in case we need to use it)
    - Unschedule section we are trying to create a backup plan for
    - Remove previously unscheduled section from pool of available Sections
        - If there aren't enough sections (ie., There were only 2 sections and its the second backup) 
          then start using the sections marked as not an option (Better to have a bad plan than none)
        - If there are multiple sections marked as not an option ask user to create ranked preference list
            - Make sure to explain why we are presenting bad choices
        - If there are no sections marked as not an option then just give up.
    - Move all sections up 1 in the preference list
    - With this new dataset run scheduling algorithm described above
- Present user with final schedules
    - Show user optimal schedule
    - Allow user to tweak preferences and rerun scheduling
        - Give option to run without creating backups if that takes a while
    - Also list backup plans
        - Make selectable
        - When selected an area shows the differences between the backup and the main schedule
        - Shows schedule
- Save a text file with the "Battleplan":
    - Broken down by Course, for each Instruction Type
        - CRN to register for
        - Backups
            - New CRN
            - Other changes
            
# Work system
This system stores the state necessary to start any "work load" from any point. This system 
 will be useful for:
 - Ensuring urls are only scrapped once
 - Making the program resumable from any point (Which also makes it failure tolerant)
 - Configure certain workloads to be retryable
 
 Here is how it is done:
 - "Scraper Status" collection, columns:
    - Scraper Name
        - Course Catalog
            - Meta: CId
        - TMS Search
            - Meta: Yr, Qrt, CTitle
        - Course One Time
            - Meta: Cid, CRN
        - Section Details
            - Meta: CRN
    - Meta
        - Holds specific information about what scraper was scraping. 
        - Follows format based on Scraper Name.
        - See Scraper Name bullet above for specific meta values stored based on Scraper Name.
    - Status
        - Queued
            - Assumed to be for an update if Last Scraped is set
            - If not set than assumed to be first time
        - In Progress
            - Same rules apply as Queued
        - Complete
    - Last Scraped
- TODO WORK

# `config.yaml`
This is a configuration file for the program. 

The main purpose of this file is to configure which courses you have to schedule and which quarter you 
want to schedule them in.

Configuration fields:

- `year`
    - **Mandatory**
    - Specifies which year to schedule in
    - Must be 2, 2 digit years separated by a dash
    - Ex., `16-17` for the 2016-2017 academic year, `17-18` for the 2017-2018 academic year
- `quarter`
    - **Mandatory**
    - Identifies which quarter to schedule in
    - Valid values are
        - `fall`
        - `winter`
        - `spring`
        - `summer`
- `courses`
    - **Mandatory**
    - Identifies which courses to schedule
    - List of objects with follow fields:
        - `subject`
            - **Mandatory**
            - 4 letter code
            - Identifies course subject
            - Ex., `PHYS` for Physics, `MATH` for Math
        - `course`
            - **Mandatory**
            - 3 number code
            - Identifies course in sequence
            - Ex., `101` or `102`
        - `types`
            - *Optional*
                - Program will automatically create a list of Instruction Types for each Course 
                - If the program's list doesn't match this list then an error will be thrown.
                - Used as a way to verify the program is working correctly for Courses which are made up of multiple 
                  Sections with different Instruction Types.
                    - If a course is made up of a single Section (ex., Just a lecture) then this field is not necessary
            - List of Instruction Types which make up this course
            - Valid values are
                - `recitation`
                - `lab`
                - `lecture`
            - Ex.,
                ```yaml
                - ...
                  types:
                    - lab
                    - lecture
                ```
        - `crns`
            - *Optional*
            - Priority list of CRNs for each Instruction Type the Course requires
                - If you must schedule a section with a specific CRN you can surround that CRN with quotes and exclamation marks.
                - Make sure you only put one CRN for that section if you do this (Otherwise the program will throw an error)
                - This is useful when Drexel schedules you in a class that you can't change like COOP 101 or CS 103 Lab.
            - Ex., 
                - You are automatically scheduled for a lab with CRN `1234567`.
                    - Additionally you **must** take this lab because you have to stay with your lab group from last term
                    - To signify this we will surround the CRN with quotes and exclamation marks
                - You would like to attend a lecture with your friend with CRN `7654321`.
                - If that lecture isn't free another friend is attending a lecture with CRN `1010101`.
                ```yaml
                - ...
                  crns:
                    - lab
                      - "!1234567!"
                    - lecture
                      - 7654321
                      - 1010101
                ```
Example `config.yaml`, configures program to schedule:

- In the Spring quarter of the 2016-2017 academic year
- Courses
    - CS 172
        - Lab
        - Lecture
    - CI 103
        - Lab
            - With mandatory CRN `1234567`
            - Must stay with lab group from CI 102
        - Lecture
    - MATH 201
        - Lecture
    - ENGL 103
        - Lecture
    - COOP 101
        - Lecture
            - With CRN `7654321`
            - Automatically scheduled by Drexel
    - UNIV 102
        - Lecture
            - With preferred CRN `1010101`
            - To have a good teacher

```yaml
- year: 16-17
- quarter: spring
- courses:
    - subject: CS
      course: 172
      types:
        - lab
        - lecture
    - subject: CI
      course: 103
      types:
        - lab
        - lecture
      crns:
        - lab
          - "!1234567!"
    - subject: MATH
      course: 201
    - subject: ENGL
      course: 103
    - subject: COOP
      course: 101
    - subject: UNIV
      course: 102
      crns:
        - lecture
          - 1010101
```
