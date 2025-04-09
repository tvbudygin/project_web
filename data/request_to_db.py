class DataBase:
    def __init__(self, User, Food, db_session):
        self.User = User
        self.Food = Food
        self.db_session = db_session

    def db_history(self, current_user):
        hist = []
        db_sess = self.db_session.create_session()
        admins = db_sess.query(self.User).filter(self.User.id == current_user.id).first()
        food = db_sess.query(self.Food).filter(self.Food.user_id == current_user.id,
                                               self.Food.result_his.isnot(None)).all()
        for i in food:
            hist.append([i.history, i.result_his])
        params = {"quant": len(hist), "hist": hist}
        if admins.admin:
            user_hist = []
            user_food = db_sess.query(self.Food).filter(self.Food.user_id == self.User.id,
                                                        self.Food.like == None, self.Food.like_title == None).all()
            for i in user_food:
                name_user = db_sess.query(self.User).filter(self.User.id == i.user_id).first()
                done_user = False
                for e in user_hist:
                    if name_user.email in e:
                        done_user = True
                        e[1] += 1
                        break
                if not done_user and name_user.email != current_user.email:
                    user_hist.append([name_user.email, 1])
            params["user_quant"] = len(user_hist)
            params["user_hist"] = user_hist
            params["admin"] = True
        return params

    def db_likes(self, current_user):
        from sqlalchemy import or_

        like = []
        db_sess = self.db_session.create_session()
        food = db_sess.query(self.Food).filter(self.Food.user_id == current_user.id,
                                               or_(self.Food.like_title.isnot(None), self.Food.like.isnot(None))).all()
        for i in food:
            like.append([i.like_title, i.like])
        return like[::-1]

    def db_delete_user(self, user_email):
        db_sess = self.db_session.create_session()
        user = db_sess.query(self.User).filter(self.User.email == user_email).first()
        if user:
            food = db_sess.query(self.Food).filter(self.Food.user_id == user.id)
            for i in food:
                db_sess.delete(i)
        db_sess.delete(user)
        db_sess.commit()

    def db_delete_yourself(self, current_user):
        db_sess = self.db_session.create_session()
        food = db_sess.query(self.Food).filter(self.Food.user_id == current_user.id).all()
        user = db_sess.query(self.User).filter(self.User.id == current_user.id).first()
        db_sess.delete(user)
        for i in food:
            db_sess.delete(i)
        db_sess.commit()

    def db_profile(self, current_user):
        db_sess = self.db_session.create_session()
        user = db_sess.query(self.User).filter(self.User.id == current_user.id).first()
        params = {"name": user.name,
                  "email": user.email,
                  "create_data": user.created_date}
        return params

    def db_main_btn_render(self, current_user, product, wish, gpt):
        db_sess = self.db_session.create_session()
        text = gpt(product, wish).split("\n")
        params = {"text": "left", "pad": "20px"}
        text1 = []
        res_his = []
        k = 1
        for i in text:
            if i != "":
                text1.append(i)
            else:
                if k <= 3:
                    params["option" + str(k)] = "<br>".join(text1)
                    res_his.append(text1[0][:-1])
                    k += 1
                text1 = []
        params["option" + str(k)] = "<br>".join(text1)
        res_his.append(text1[0][:-1])
        food = self.Food(
            history=f"{product}; {wish}" if product != "" and wish != "" else f"{product}{wish}",
            user_id=current_user.id,
            result_his=", ".join(res_his)
        )
        db_sess.add(food)
        db_sess.commit()
        return params

    def db_main_btn_like(self, request, current_user):
        db_sess = self.db_session.create_session()
        like_text = request.form.get("like")
        if ("1 Вариант Рецепта" != like_text and "2 Вариант Рецепта" != like_text
                and "3 Вариант Рецепта" != like_text):
            params = {"text": "left", "pad": "20px", "option1": request.form.get("option1"),
                      "option2": request.form.get("option2"), "option3": request.form.get("option3")}
            food = self.Food(
                like_title=like_text[like_text.find(".") + 2:like_text.find("<br>") - 1],
                like=like_text[like_text.find("<br>") + 4:],
                user_id=current_user.id
            )
            db_sess.add(food)
            db_sess.commit()
            return params