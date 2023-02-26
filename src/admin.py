import dal


def delete_book_adm(name_obj, date, time):
    bookid = dal.get_book_id(name_obj, date, time)
    dal.delete_my_book(bookid)
