# Capstone-project 1: Booklyn



Please check out my project: [Booklyn](https://booklyn-app.herokuapp.com/)


## OVERVIEW
Booklyn is a digital book shelf where users can label books they want to read, are currently reading, have read, or favorite and they can leave reviews on the books.
## GOALS
1. Users will be able to keep track of which books they wanted to read and have read as well as what they felt when they read.
2. Help people read or access more books that interest them by the social media aspect of this app.

## USER DEMOGRAPHIC
People who like to read, want to share their thoughts about books or see other people's reviews on books.

## DATA SOURCE
Data will be sourced from the following:
- [Google Books API](https://developers.google.com/books/docs/v1/getting_started)

    
Book cover images are provided through their API as well as other information such as book titles, subtitles, authors, genre, publisher and average user ratings.
    
## DATABASE SCHEMA
![database schema](https://github.com/mariered0/29_Capstone-project1/blob/main/Documentation/Schema_Booklyn_updated.png?raw=true)

## How to Use
1. First please sign up.
2. Once you sign up, search for a book title. There will be maximum of 40 books that were hit with the term displayed.
3. Add your favorite books to your favorite list or a book to your want to read, currently reading or read list.
4. You can write a review of the books that are in your list. All of the reviews you've written can be seen from the review button in your profile page which can be accessed from your username in the nav bar.

## Features

### Only first book with same title is added to a list
Multiple books with the same title published by different publishers or different versions of the same books are displayed when you search.<br/>
![search result](https://github.com/mariered0/29_Capstone-project1/blob/main/Documentation/Images_doc/Screen Shot 2022-10-11 at 6.52.43 PM.png?raw=true)

If you add two books with the same title and same author, only the first one will be added to the list to avoid user's confusion (no dupilication).<br/>
![book added to list](https://github.com/mariered0/29_Capstone-project1/blob/main/Documentation/Images_doc/Screen Shot 2022-10-11 at 6.54.54 PM.png?raw=true)









