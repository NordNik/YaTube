from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.long_text = "This is a long text to check how str method works"
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.long_text,
        )

    def test_method_str(self):
        classes = ((PostModelTest.post, self.long_text[:15]),
                   (PostModelTest.group, 'Группа "Тестовая группа"'))
        for element, answer in classes:
            with self.subTest(element=element):
                name = str(element)
                self.assertEqual(name, answer)
